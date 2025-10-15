# -*- coding: utf-8 -*-

import geopandas
import matplotlib.pyplot as plt


print("This is Python")

# url = "https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip" # 저해상도 (1:110m)
# url = "https://naturalearth.s3.amazonaws.com/50m_cultural/ne_50m_admin_0_countries.zip"   # 중간해상도 (1:50m)
url = "https://naturalearth.s3.amazonaws.com/10m_cultural/ne_10m_admin_0_countries.zip"   # 고해상도 (1:10m)
world = geopandas.read_file(url)

# 대한민국만 필터 (이름 또는 ISO 코드)
kor = world[(world["NAME"] == "South Korea") | (world["ADM0_A3"] == "KOR")]

# 좌표계 확인
print(kor.crs)  # 보통 EPSG:4326

# 지도 표시
ax = kor.plot(edgecolor="black", figsize=(6,6))
ax.set_title("South Korea")
plt.show()