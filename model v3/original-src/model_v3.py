from __future__ import annotations
from pathlib import Path
import argparse
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import RidgeCV, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

RANDOM_SEEDS=[42,123,2026]
N_FOLDS=5
ALPHAS=np.logspace(-2,3,20)
MONTHLY_COL='is_monthly_rental(min_nights>28)'
CATEGORICAL=['neighborhood','room_type','property_type','host_tier','is_superhost_cat']
RATINGS=['rating_overall','rating_cleanliness','rating_checkin','rating_communication','rating_location','rating_value','rating_listing_accuracy']
SIZE=['max_guests','bedrooms','beds','bathrooms']

def prep(df):
    df=df.copy()
    df['is_superhost_cat']=df['is_superhost'].astype('object').where(df['is_superhost'].notna(),'unknown').astype(str)
    df['sentiment_missing']=df['sentiment_score'].isna().astype(int)
    df['sentiment_score']=df['sentiment_score'].fillna(df['sentiment_score'].median())
    return df

def numeric_features(df):
    return SIZE+RATINGS+[c for c in df.columns if c.startswith('has_')]+['sentiment_score','sentiment_missing']

def build_model(numeric):
    pre=ColumnTransformer([
        ('cat',OneHotEncoder(handle_unknown='ignore',sparse_output=False),CATEGORICAL),
        ('num',StandardScaler(),numeric)],verbose_feature_names_out=False)
    return Pipeline([('pre',pre),('model',RidgeCV(alphas=ALPHAS))])

def repeated_oof(seg_df,numeric):
    X=seg_df[CATEGORICAL+numeric]
    y=seg_df['nightly_price'].astype(float).to_numpy(); yl=np.log(y)
    # Tune alpha once on the full segment, then use fixed-alpha OOF folds.
    tuner=build_model(numeric); tuner.fit(X,yl)
    alpha=float(tuner.named_steps['model'].alpha_)
    fair=np.zeros(len(seg_df)); fold_ids=np.zeros(len(seg_df),dtype=int)
    kf=KFold(N_FOLDS,shuffle=True,random_state=42)
    for f,(tr,va) in enumerate(kf.split(X),1):
        pre=ColumnTransformer([('cat',OneHotEncoder(handle_unknown='ignore',sparse_output=True),CATEGORICAL),('num',StandardScaler(),numeric)],verbose_feature_names_out=False)
        m=Pipeline([('pre',pre),('model',Ridge(alpha=alpha))])
        m.fit(X.iloc[tr],yl[tr])
        smear=float(np.mean(np.exp(yl[tr]-m.predict(X.iloc[tr]))))
        fair[va]=np.exp(m.predict(X.iloc[va]))*smear; fold_ids[va]=f
    abs_pct=np.abs(y-fair)/y
    # Prediction uncertainty proxy: segment error adjusted by category rarity.
    base=float(np.median(abs_pct))
    rarity=np.zeros(len(seg_df))
    for c in CATEGORICAL:
        freq=seg_df[c].astype(str).map(seg_df[c].astype(str).value_counts())
        rarity += 1/np.sqrt(np.maximum(freq.to_numpy(),1))
    rarity=rarity/len(CATEGORICAL)
    rel_unc=np.clip(base*(1+2*rarity),0,1)
    pred_sd=fair*rel_unc
    return np.maximum(fair,.01),pred_sd,rel_unc,fold_ids,[alpha]

def score_confidence(rel_unc, seg_mape):
    stability=np.clip(1-rel_unc/0.25,0,1)
    model_quality=np.clip(1-seg_mape/0.60,0,1)
    score=100*(0.7*stability+0.3*model_quality)
    label=pd.cut(score,[-1,55,75,101],labels=['Low','Medium','High']).astype(str)
    return score,label

def metrics(seg,y,fair,rel_unc):
    resid=y-fair
    return dict(segment=seg,n_listings=len(y),R2_log=r2_score(np.log(y),np.log(fair)),R2_price=r2_score(y,fair),MAE_USD=mean_absolute_error(y,fair),RMSE_USD=mean_squared_error(y,fair)**.5,Median_APE=float(np.median(np.abs(resid)/y)),Median_prediction_uncertainty_pct=float(np.median(rel_unc)))

def main(input_path,outdir):
    outdir=Path(outdir); outdir.mkdir(parents=True,exist_ok=True)
    df=prep(pd.read_csv(input_path)); numeric=numeric_features(df)
    all_rows=[]; mets=[]; alpha_rows=[]
    for seg,sg in {'short_stay':df[df[MONTHLY_COL]==0].copy(),'monthly':df[df[MONTHLY_COL]==1].copy()}.items():
        fair,sd,ru,folds,alphas=repeated_oof(sg,numeric); y=sg.nightly_price.astype(float).to_numpy()
        m=metrics(seg,y,fair,ru); mets.append(m)
        conf,label=score_confidence(ru,m['Median_APE'])
        resid=y-fair
        all_rows.append(pd.DataFrame({
            'listing_id':sg.id.to_numpy(),'listing_name':sg.listing_name.to_numpy(),'listing_url':sg.listing_url.to_numpy(),
            'borough':sg.borough.to_numpy(),'neighborhood':sg.neighborhood.to_numpy(),'room_type':sg.room_type.to_numpy(),
            'property_type':sg.property_type.to_numpy(),'host_tier':sg.host_tier.to_numpy(),'market_segment':seg,
            'actual_price_usd':np.round(y,2),'predicted_fair_price_usd':np.round(fair,2),'prediction_sd_usd':np.round(sd,2),
            'prediction_uncertainty_pct':np.round(ru,4),'confidence_score':np.round(conf,1),'confidence_level':label,
            'residual_usd':np.round(resid,2),'residual_pct_of_fair':np.round(resid/fair,4),
            'pricing_signal':np.where(resid>0,'Above fair value (review price)',np.where(resid<0,'Below fair value (review price)','At fair value'))
        }))
        alpha_rows.append({'segment':seg,'median_selected_alpha':float(np.median(alphas)),'min_alpha':float(np.min(alphas)),'max_alpha':float(np.max(alphas))})
    res=pd.concat(all_rows,ignore_index=True); met=pd.DataFrame(mets)
    res.to_csv(outdir/'v3_listing_pricing_signals.csv',index=False)
    met.to_csv(outdir/'v3_segment_metrics.csv',index=False)
    pd.DataFrame(alpha_rows).to_csv(outdir/'v3_alpha_stability.csv',index=False)
    # segment diagnostics for slides
    diag=(res.groupby(['market_segment','host_tier','borough'],dropna=False)
          .agg(n_listings=('listing_id','size'),median_abs_residual_usd=('residual_usd',lambda x: float(np.median(np.abs(x)))),
               median_confidence=('confidence_score','median'),median_uncertainty_pct=('prediction_uncertainty_pct','median'))
          .reset_index())
    diag.to_csv(outdir/'v3_segment_diagnostics.csv',index=False)
    print(met.to_string(index=False))

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--input',type=Path,required=True); p.add_argument('--output-dir',type=Path,required=True); a=p.parse_args(); main(a.input,a.output_dir)
