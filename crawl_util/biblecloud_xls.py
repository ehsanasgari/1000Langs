


iso_cloud_not_found=set([x for x in list(mapping.keys()) if len(df[df['code']==x]['iso'].tolist())==0])
