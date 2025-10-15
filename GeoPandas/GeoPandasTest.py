# -*- coding: utf-8 -*-

import geopandas
import matplotlib.pyplot as plt


print("This is Python")

# url = "https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip" # ���ػ� (1:110m)
# url = "https://naturalearth.s3.amazonaws.com/50m_cultural/ne_50m_admin_0_countries.zip"   # �߰��ػ� (1:50m)
url = "https://naturalearth.s3.amazonaws.com/10m_cultural/ne_10m_admin_0_countries.zip"   # ���ػ� (1:10m)
world = geopandas.read_file(url)

# ���ѹα��� ���� (�̸� �Ǵ� ISO �ڵ�)
kor = world[(world["NAME"] == "South Korea") | (world["ADM0_A3"] == "KOR")]

# ��ǥ�� Ȯ��
print(kor.crs)  # ���� EPSG:4326

# ���� ǥ��
ax = kor.plot(edgecolor="black", figsize=(6,6))
ax.set_title("South Korea")
plt.show()