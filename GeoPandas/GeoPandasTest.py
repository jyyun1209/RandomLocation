# -*- coding: utf-8 -*-

import sys
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import Point
from shapely.ops import unary_union


print("This is Python")

# url = "https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip" # ���ػ� (1:110m)
# url = "https://naturalearth.s3.amazonaws.com/50m_cultural/ne_50m_admin_0_countries.zip"   # �߰��ػ� (1:50m)
url = "https://naturalearth.s3.amazonaws.com/10m_cultural/ne_10m_admin_0_countries.zip"   # ���ػ� (1:10m)
world = gpd.read_file(url)

# ���ѹα��� ���� (�̸� �Ǵ� ISO �ڵ�)
kor = world[(world["NAME"] == "South Korea") | (world["ADM0_A3"] == "KOR")]

# # ��ǥ�� Ȯ��
# print(kor.crs)  # ���� EPSG:4326

# # ���� ǥ��
# ax = kor.plot(edgecolor="black", figsize=(6,6))
# ax.set_title("South Korea")
# plt.show()

aea_korea = (
    "+proj=aea +lat_1=25 +lat_2=47 +lat_0=33 +lon_0=127 "
    "+x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs"
)
kor_proj = kor.to_crs(aea_korea)

# ������(Ȥ�� ��Ƽ������) �غ�
poly = unary_union(kor_proj.geometry.values)

def random_points_in_polygon(polygon, n):
    # """���� ��ǥ�� �� polygon ���ο� �յ� ������ �� n�� ����(���� ���ø�)."""
    minx, miny, maxx, maxy = polygon.bounds
    pts = []
    # �ڽ� ��� ������ ���� ������ ���� �ݺ� Ƚ���� �ٸ� �� ����
    while len(pts) < n:
        xs = np.random.uniform(minx, maxx, size=n*2)  # ���� �ְ� �̱�
        ys = np.random.uniform(miny, maxy, size=n*2)
        cand = [Point(x, y) for x, y in zip(xs, ys)]
        for p in cand:
            if polygon.contains(p):
                pts.append(p)
                if len(pts) == n:
                    break
    return pts

# 3) ���ϴ� ���� ����
N = 1  # ��: 100�� ��ǥ
pts_proj = random_points_in_polygon(poly, N)

# 4) GeoDataFrame���� ����� �ٽ� ������(EPSG:4326)�� ��ȯ
gdf_pts = gpd.GeoDataFrame(geometry=gpd.GeoSeries(pts_proj, crs=aea_korea)).to_crs(4326)

# ��� Ȯ��
# print(gdf_pts.head())

# �ʿ� �� CSV�� �������� (lon, lat)
# gdf_pts["lon"] = gdf_pts.geometry.x
# gdf_pts["lat"] = gdf_pts.geometry.y
# gdf_pts[["lon", "lat"]].to_csv("random_points_korea.csv", index=False)
# print("saved: random_points_korea.csv")


sgg = gpd.read_file("sig.shp")   # �ñ���
if sgg.crs is None:
    sgg = sgg.set_crs(5179)   # ��ǥ�� ���� ����, �󺧸� ����
sgg = sgg.to_crs(4326)
print("sgg.crs =", sgg.crs)
print("bounds = ", sgg.total_bounds)
# emd = gpd.read_file("EMD.shp").to_crs(4326)   # ���鵿 (����)

# 2) ���� ��ǥ(�̹� ���ϼ̴� ������ ���ø�)
lon, lat = gdf_pts.geometry.x, gdf_pts.geometry.y
# pt_gdf = gpd.GeoDataFrame([{"geometry": Point(lon, lat)}], crs=4326)
pt_gdf = gdf_pts.iloc[[0]]

# 3) ����Ʈ�� ���Ե� ������ ã�� (��Ȯ)
#hit_sgg = gpd.sjoin(pt_gdf, sgg, how="left", predicate="within")
# hit_emd = gpd.sjoin(pt_gdf, emd, how="left", predicate="within")

# 4) �÷� �̸��� ���� �����Ϳ� �°� �����ϼ���.
# ���� SIDO_NM / SIG_KOR_NM / EMD_KOR_NM ���� �ѱ� �÷��� �ֽ��ϴ�.
#sido = hit_sgg.iloc[0].get("SIDO_NM")
#sigungu = hit_sgg.iloc[0].get("SIG_KOR_NM")
# eup_myeon_dong = hit_emd.iloc[0].get("EMD_KOR_NM")

# 3) ���� ����
hit_sgg = gpd.sjoin(pt_gdf, sgg, how="left", predicate="within")

# 4) ���� �÷��� Ȯ�� �� ��������
print("cols:", hit_sgg.columns.tolist())   # ���� �� ��Ȯ�� �̸� Ȯ��
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