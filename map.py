import geopandas as gp
import matplotlib.pyplot as plt
import pandas as pd

states = gp.read_file('/workspace/cobalt/tl_2014_us_state.shp')
type(states)

states.head()
states.crs
states = states.to_crs("EPSG:3395")

cities = pd.read_csv('/workspace/cobalt/UScities.csv', header = 0, index_col= 0,names=[`city`, `lat`, `lng`, `stateId`, `stateName`, `countyName`, `countyFips`])

states.plot()
plt.show()

plt.savefig('plswork.png')