from pathlib import Path
import argparse
import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
MIN_TIER_COHORT=15; MIN_BASE_COHORT=15; N_NEIGHBORS=30; TOP_Q=.67
MONTHLY_COL='is_monthly_rental(min_nights>28)'

def main(input_path,pricing_path,outdir):
    outdir=Path(outdir); outdir.mkdir(parents=True,exist_ok=True)
    df=pd.read_csv(input_path); pricing=pd.read_csv(pricing_path)
    df['market_segment']=np.where(df[MONTHLY_COL]==1,'monthly','short_stay')
    df['base_cohort']=df['segment'].astype(str)+' | '+df['market_segment']
    df['tier_cohort']=df['base_cohort']+' | '+df['host_tier'].astype(str)
    amen=[c for c in df.columns if c.startswith('has_')]
    amen_arr=df[amen].fillna(0).to_numpy(dtype=float)
    feats=['max_guests','bedrooms','beds','bathrooms','latitude','longitude']+amen
    X=StandardScaler().fit_transform(df[feats].fillna(df[feats].median()))
    seg_nn={}
    for ms,idx in df.groupby('market_segment',sort=False).groups.items():
        pos=np.asarray(list(idx),dtype=int); k=min(N_NEIGHBORS+1,len(pos)); seg_nn[ms]=(pos,NearestNeighbors(n_neighbors=k).fit(X[pos]))
    tier_groups={k:np.asarray(list(v),dtype=int) for k,v in df.groupby('tier_cohort',sort=False).groups.items()}
    base_groups={k:np.asarray(list(v),dtype=int) for k,v in df.groupby('base_cohort',sort=False).groups.items()}
    occ=df.occupancy_rate.to_numpy(dtype=float); ids=df.id.to_numpy(); tiers=df.host_tier.astype(str).to_numpy(); markets=df.market_segment.to_numpy(); tkeys=df.tier_cohort.to_numpy(); bkeys=df.base_cohort.to_numpy()
    rows=[]
    for i in range(len(df)):
        tier_pos=tier_groups[tkeys[i]]; base_pos=base_groups[bkeys[i]]
        if len(tier_pos)>=MIN_TIER_COHORT: peers=tier_pos[tier_pos!=i]; method='host_tier_exact_cohort'; key=tkeys[i]
        elif len(base_pos)>=MIN_BASE_COHORT: peers=base_pos[base_pos!=i]; method='base_exact_cohort'; key=bkeys[i]
        else:
            pos,nn=seg_nn[markets[i]]; _,nbr=nn.kneighbors(X[i:i+1]); peers=np.array([pos[p] for p in nbr[0] if pos[p]!=i]); method='knn_fallback'; key=bkeys[i]
        po=occ[peers]; cutoff=np.quantile(po,TOP_Q); high=peers[po>=cutoff]
        if len(high)==0: high=peers
        share=amen_arr[high].mean(axis=0) if len(high) else np.zeros(len(amen))
        missing=[amen[k].replace('has_','') for k in range(len(amen)) if share[k]>=.60 and amen_arr[i,k]==0]
        peer_support=min(len(peers)/50,1); match_quality={'host_tier_exact_cohort':1,'base_exact_cohort':.8,'knn_fallback':.6}[method]
        ph=float(np.mean(occ[high])) if len(high) else np.nan
        rows.append((ids[i],tiers[i],markets[i],key,method,len(peers),len(high),round(100*(.6*peer_support+.4*match_quality),1),round(float(occ[i]),1),round(ph,1) if np.isfinite(ph) else np.nan,round(ph-occ[i],1) if np.isfinite(ph) else np.nan,'; '.join(missing) if missing else '(none)',len(missing)))
    cols=['listing_id','host_tier','market_segment','cohort_key','match_method','n_peers','n_high_performers','peer_support_score','my_occupancy_days','peer_high_occupancy_days','occupancy_gap_days','missing_amenities_vs_peers','n_missing_amenities']
    out=pd.DataFrame(rows,columns=cols).merge(pricing,on='listing_id',how='left')
    out['overall_recommendation_confidence']=np.round(.65*out.confidence_score+.35*out.peer_support_score,1)
    out.to_csv(outdir/'v3_knn_recommendations.csv',index=False)
    print(out.match_method.value_counts().to_string())

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--input',type=Path,required=True); p.add_argument('--pricing',type=Path,required=True); p.add_argument('--output-dir',type=Path,required=True); a=p.parse_args(); main(a.input,a.pricing,a.output_dir)
