# -*- coding: utf-8 -*-

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import Point
from shapely.ops import unary_union


print("This is Python")

# url = "https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip" # 저해상도 (1:110m)
# url = "https://naturalearth.s3.amazonaws.com/50m_cultural/ne_50m_admin_0_countries.zip"   # 중간해상도 (1:50m)
url = "https://naturalearth.s3.amazonaws.com/10m_cultural/ne_10m_admin_0_countries.zip"   # 고해상도 (1:10m)
world = gpd.read_file(url)

# 대한민국만 필터 (이름 또는 ISO 코드)
kor = world[(world["NAME"] == "South Korea") | (world["ADM0_A3"] == "KOR")]

# # 좌표계 확인
# print(kor.crs)  # 보통 EPSG:4326

# # 지도 표시
# ax = kor.plot(edgecolor="black", figsize=(6,6))
# ax.set_title("South Korea")
# plt.show()

aea_korea = (
    "+proj=aea +lat_1=25 +lat_2=47 +lat_0=33 +lon_0=127 "
    "+x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs"
)
kor_proj = kor.to_crs(aea_korea)

# 폴리곤(혹은 멀티폴리곤) 준비
poly = unary_union(kor_proj.geometry.values)

def random_points_in_polygon(polygon, n):
    # """투영 좌표계 상 polygon 내부에 균등 무작위 점 n개 생성(거절 샘플링)."""
    minx, miny, maxx, maxy = polygon.bounds
    pts = []
    # 박스 대비 폴리곤 면적 비율에 따라 반복 횟수는 다를 수 있음
    while len(pts) < n:
        xs = np.random.uniform(minx, maxx, size=n*2)  # 여유 있게 뽑기
        ys = np.random.uniform(miny, maxy, size=n*2)
        cand = [Point(x, y) for x, y in zip(xs, ys)]
        for p in cand:
            if polygon.contains(p):
                pts.append(p)
                if len(pts) == n:
                    break
    return pts

# 3) 원하는 개수 설정
N = 1000  # 예: 100개 좌표
pts_proj = random_points_in_polygon(poly, N)

# 4) GeoDataFrame으로 만들고 다시 경위도(EPSG:4326)로 변환
gdf_pts = gpd.GeoDataFrame(geometry=gpd.GeoSeries(pts_proj, crs=aea_korea)).to_crs(4326)

# 결과 확인
# print(gdf_pts.head())

# 필요 시 CSV로 내보내기 (lon, lat)
# gdf_pts["lon"] = gdf_pts.geometry.x
# gdf_pts["lat"] = gdf_pts.geometry.y
# gdf_pts[["lon", "lat"]].to_csv("random_points_korea.csv", index=False)
# print("saved: random_points_korea.csv")

ax = kor.plot(edgecolor="k", facecolor="none", figsize=(6,6))
gdf_pts.plot(ax=ax, markersize=5)
plt.show()