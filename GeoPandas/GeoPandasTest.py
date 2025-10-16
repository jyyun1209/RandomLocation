# -*- coding: utf-8 -*-

import sys
import threading
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import Point
from shapely.ops import unary_union

plt.ion()
print("This is Python")

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


N = 1
pts_proj = random_points_in_polygon(poly, N)


gdf_pts = gpd.GeoDataFrame(geometry=gpd.GeoSeries(pts_proj, crs=aea_korea)).to_crs(4326)
print(gdf_pts.head())


# gdf_pts["lon"] = gdf_pts.geometry.x
# gdf_pts["lat"] = gdf_pts.geometry.y
# gdf_pts[["lon", "lat"]].to_csv("random_points_korea.csv", index=False)
# print("saved: random_points_korea.csv")

sd = gpd.read_file("ctprvn.shp") # 시도
sgg = gpd.read_file("sig.shp")   # 시군구

if sd.crs is None:
    sd = sd.set_crs(5179)
if sgg.crs is None:
    sgg = sgg.set_crs(5179)
sd = sd.to_crs(4326)
sgg = sgg.to_crs(4326)

print("sd.crs =", sd.crs)
print("sgg.crs =", sgg.crs)
print("sd bounds = ", sd.total_bounds)
print("sgg bounds = ", sgg.total_bounds)


lon, lat = gdf_pts.geometry.x, gdf_pts.geometry.y
pt_gdf = gdf_pts.iloc[[0]]


hit_sd = gpd.sjoin(pt_gdf, sd, how="left", predicate="within")
hit_sgg = gpd.sjoin(pt_gdf, sgg, how="left", predicate="within")


print("cols:", hit_sd.columns.tolist())
print("cols:", hit_sgg.columns.tolist())

sido = hit_sd.iloc[0].get("CTP_ENG_NM")
sigungu = hit_sgg.iloc[0].get("SIG_ENG_NM")
print(sido, sigungu)

ax = kor.plot(edgecolor="k", facecolor="none", figsize=(6,6))
gdf_pts.plot(ax=ax, markersize=5, color="red")
plt.show()