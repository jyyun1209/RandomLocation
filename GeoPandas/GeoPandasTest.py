# -*- coding: utf-8 -*-

import io
import sys
import threading
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import Point
from shapely.ops import unary_union
import json
import time
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

# print("This is Python")

# url = "https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip"
# url = "https://naturalearth.s3.amazonaws.com/50m_cultural/ne_50m_admin_0_countries.zip"
url = "https://naturalearth.s3.amazonaws.com/10m_cultural/ne_10m_admin_0_countries.zip"
world = gpd.read_file(url)

kor = world[(world["NAME"] == "South Korea") | (world["ADM0_A3"] == "KOR")]

# print(kor.crs)

# ax = kor.plot(edgecolor="black", figsize=(6,6))
# ax.set_title("South Korea")
# plt.show()

aea_korea = (
    "+proj=aea +lat_1=25 +lat_2=47 +lat_0=33 +lon_0=127 "
    "+x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs"
)
kor_proj = kor.to_crs(aea_korea)

poly = unary_union(kor_proj.geometry.values)

def random_points_in_polygon(polygon, n):
    minx, miny, maxx, maxy = polygon.bounds
    pts = []
    while len(pts) < n:
        xs = np.random.uniform(minx, maxx, size=n*2)
        ys = np.random.uniform(miny, maxy, size=n*2)
        cand = [Point(x, y) for x, y in zip(xs, ys)]
        for p in cand:
            if polygon.contains(p):
                pts.append(p)
                if len(pts) == n:
                    break
    return pts


N = 20
pts_proj = random_points_in_polygon(poly, N)


gdf_pts = gpd.GeoDataFrame(geometry=gpd.GeoSeries(pts_proj, crs=aea_korea)).to_crs(4326)
# print(gdf_pts.head())


# gdf_pts["lon"] = gdf_pts.geometry.x
# gdf_pts["lat"] = gdf_pts.geometry.y
# gdf_pts[["lon", "lat"]].to_csv("random_points_korea.csv", index=False)
# print("saved: random_points_korea.csv")

sd = gpd.read_file("ctprvn.shp", encoding="cp949") # 시도
sgg = gpd.read_file("sig.shp" ,encoding="cp949")   # 시군구

if sd.crs is None:
    sd = sd.set_crs(5179)
if sgg.crs is None:
    sgg = sgg.set_crs(5179)
sd = sd.to_crs(4326)
sgg = sgg.to_crs(4326)

# print("sd.crs =", sd.crs)
# print("sgg.crs =", sgg.crs)
# print("sd bounds = ", sd.total_bounds)
# print("sgg bounds = ", sgg.total_bounds)


lon, lat = gdf_pts.geometry.x, gdf_pts.geometry.y

for i, pt_gdf in gdf_pts.iterrows():
    lon = float(pt_gdf.geometry.x)
    lat = float(pt_gdf.geometry.y)

    single_gdf = gpd.GeoDataFrame([pt_gdf], geometry=[pt_gdf.geometry], crs=gdf_pts.crs)

    # 행정구역 찾기
    hit_sd = gpd.sjoin(single_gdf, sd, how="left", predicate="within")
    hit_sgg = gpd.sjoin(single_gdf, sgg, how="left", predicate="within")

    sido_eng = hit_sd.iloc[0].get("CTP_ENG_NM")
    sigungu_eng = hit_sgg.iloc[0].get("SIG_ENG_NM")
    sido_kor = hit_sd.iloc[0].get("CTP_KOR_NM")
    sigungu_kor = hit_sgg.iloc[0].get("SIG_KOR_NM")

    name = f"{sido_kor or ''} {sigungu_kor or ''}".strip()

    # out = Path("check_utf8.json")
    # with out.open("w", encoding="utf-8", newline="\n") as f:
    #     json.dump({"lat": lat, "lon": lon, "name": name}, f, ensure_ascii=False, indent=2)
        
    print(json.dumps({"lat": lat, "lon": lon, "name": name}, ensure_ascii=False), flush=True)
    time.sleep(0.8)
    
# pt_gdf = gdf_pts.iloc[[0]]

# hit_sd = gpd.sjoin(pt_gdf, sd, how="left", predicate="within")
# hit_sgg = gpd.sjoin(pt_gdf, sgg, how="left", predicate="within")


# # print("cols:", hit_sd.columns.tolist())
# # print("cols:", hit_sgg.columns.tolist())

# sido = hit_sd.iloc[0].get("CTP_ENG_NM")
# sigungu = hit_sgg.iloc[0].get("SIG_ENG_NM")
# # print(sido, sigungu)

# name = f"{sido} {sigungu}"
# print(json.dumps({"lat": float(lat), "lon": float(lon), "name": name}, ensure_ascii=False), flush=True)

# ax = kor.plot(edgecolor="k", facecolor="none", figsize=(6,6))
# gdf_pts.plot(ax=ax, markersize=5, color="red")
# plt.show()