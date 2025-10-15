# -*- coding: utf-8 -*-

import sys
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
N = 1  # 예: 100개 좌표
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


sgg = gpd.read_file("sig.shp")   # 시군구
if sgg.crs is None:
    sgg = sgg.set_crs(5179)   # 좌표값 변경 없음, 라벨만 붙임
sgg = sgg.to_crs(4326)
print("sgg.crs =", sgg.crs)
print("bounds = ", sgg.total_bounds)
# emd = gpd.read_file("EMD.shp").to_crs(4326)   # 읍면동 (선택)

# 2) 랜덤 좌표(이미 구하셨다 했으니 예시만)
lon, lat = gdf_pts.geometry.x, gdf_pts.geometry.y
# pt_gdf = gpd.GeoDataFrame([{"geometry": Point(lon, lat)}], crs=4326)
pt_gdf = gdf_pts.iloc[[0]]

# 3) 포인트가 포함된 폴리곤 찾기 (정확)
#hit_sgg = gpd.sjoin(pt_gdf, sgg, how="left", predicate="within")
# hit_emd = gpd.sjoin(pt_gdf, emd, how="left", predicate="within")

# 4) 컬럼 이름은 보유 데이터에 맞게 조정하세요.
# 흔히 SIDO_NM / SIG_KOR_NM / EMD_KOR_NM 같은 한글 컬럼이 있습니다.
#sido = hit_sgg.iloc[0].get("SIDO_NM")
#sigungu = hit_sgg.iloc[0].get("SIG_KOR_NM")
# eup_myeon_dong = hit_emd.iloc[0].get("EMD_KOR_NM")

# 3) 공간 조인
hit_sgg = gpd.sjoin(pt_gdf, sgg, how="left", predicate="within")

# 4) 실제 컬럼명 확인 후 가져오기
print("cols:", hit_sgg.columns.tolist())   # 여기 찍어서 정확한 이름 확인
# sido = hit_sgg.iloc[0].get("SIDO_NM") or hit_sgg.iloc[0].get("CTP_KOR_NM")
# sigungu = hit_sgg.iloc[0].get("SIG_KOR_NM") or hit_sgg.iloc[0].get("SIG_ENG_NM")
sigungu = hit_sgg.iloc[0].get("SIG_ENG_NM")

# print(f"{sido} {sigungu} {eup_myeon_dong}")
def safe_print(s):
    enc = sys.stdout.encoding or "cp949"
    print(str(s).encode(enc, errors="replace").decode(enc, errors="replace"))

safe_print(f"{sigungu}")

ax = kor.plot(edgecolor="k", facecolor="none", figsize=(6,6))
gdf_pts.plot(ax=ax, markersize=5, color="red")
plt.show()