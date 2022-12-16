import streamlit as st
import pandas as pd
import json
import matplotlib.pyplot as plt
import numpy as np
import base64
import math
import datetime
import seaborn as sns

st.title("Volcano Data")

# Load the volcano data
data = pd.read_csv("volcano_data.csv")

# Create a sidebar
st.sidebar.title("Select volcano")
volcano_name = st.sidebar.selectbox("Volcano name", data["Volcano Name"])

st.sidebar.title('Filter points')

bce_ce = st.sidebar.selectbox("Time Period", ['BCE', 'CE'])

eruption_Dates = data['Last Known Eruption']

# Function that trims BCE/CE dates into integers
def extractYearsFromdf(eruption_Dates, bc_or_ce_string):
	return [int(dates.replace(bc_or_ce_string, '')) for dates in eruption_Dates if bc_or_ce_string in dates]


dates_BCE = extractYearsFromdf(eruption_Dates, ' BCE')
dates_CE = extractYearsFromdf(eruption_Dates, ' CE')

if bce_ce == 'CE':
	year = st.sidebar.slider("Last Known Eruption (<= this year)", 
		min_value=0, max_value=max(dates_CE))
else:
	year = st.sidebar.slider("Last Known Eruption (<= this year)", 
		min_value=0, max_value=max(dates_BCE))

# Add a header with the name of the selected volcano
st.header(volcano_name)

# Add a link to more information about the selected volcano
st.write(f'See [{volcano_name}](<https://en.wikipedia.org/wiki/{volcano_name}>) for more '
		 f'information about {volcano_name}')

#Add a button to download the data
#if st.button("Download data"):
#    st.write("Downloading data...")

with st.echo():
	# Display selected volcano directly on the map:
	selected_data = data[data['Volcano Name'] == volcano_name]
	selected_data = selected_data[['Latitude', 'Longitude']]
	selected_data = selected_data.rename(columns={'Latitude':'lat', 'Longitude': 'lon'})
	st.map(selected_data)


# Add a header with the name of the filtered volcanos:
st.header('Filtered Volcanos')

with st.echo():
	# TRY THE YEAR SLIDER TO CHANGE THIS MAP:
	# Handle differently if BCE or CE period is selected:
	
	data_ = data.copy()
	data_ = data_[~data_['Last Known Eruption'].str.contains('Unknown')]
	
	if bce_ce == 'BCE':
		data_ = data_[data_['Last Known Eruption'].str.contains('BCE')]
		lke = data_['Last Known Eruption']
		lke = lke.str.replace(' BCE','')
		data_['Last Known Eruption'] = lke
		data_ = data_[data_['Last Known Eruption'].astype(int) <= year]
		
	else:
		data_['Last Known Eruption'] = data_['Last Known Eruption'].str.replace(' BCE','00000')
		lke = data_['Last Known Eruption']
		lke = lke.str.replace(' CE','')
		data_['Last Known Eruption'] = lke
		data_ = data_[(data_['Last Known Eruption'].astype(int) <= year) |
					  (data_['Last Known Eruption'].astype(int) > datetime.date.today().year)]

	# Display selected volcano directly on the map:
	selected_data = data_[['Latitude', 'Longitude']]
	selected_data = selected_data.rename(columns={'Latitude':'lat', 'Longitude': 'lon'})
	st.map(selected_data)	

st.header('Volcano Statistics/Miscellaneous')

with st.echo():
	# Display a heatmap of the elevation data:
	import leafmap.foliumap as leafmap
	m = leafmap.Map(tiles='stamentoner')
	selected_data = data[data['Volcano Name'] == volcano_name]
	selected_data = data[['Latitude', 'Longitude', 'Elevation']]
	m.add_heatmap(selected_data, latitude="Latitude", longitude='Longitude', value="Elevation",
				  name="Heat map", radius=10)
	m.to_streamlit(width=700, height=500, add_layer_control=True)


with st.echo():
	# Display gif:
	file_ = open('volcano_eruption.gif', 'rb')
	contents = file_.read()
	data_url = base64.b64encode(contents).decode('utf-8')
	file_.close()
	st.markdown(f'<img src="data:image/gif;base64,{data_url}" alt="cat gif">',
    	unsafe_allow_html=True)

with st.echo():
	# Create a stacked bar chart showing the number of active and inactive volcanoes in each region:
	data_ = data.dropna(subset=['Activity Evidence'])
	regions = data_['Region'].unique()
	activity_evidence = data_['Activity Evidence'].unique()

	activity_counts = {}

	for region in regions:
		d_ = {}
		for evidence_level in activity_evidence:
			cnt = data[(data_['Activity Evidence']==evidence_level)&(data['Region'] == region)]
			cnt = len(cnt)
			d_[evidence_level] = cnt
		activity_counts[region] = d_

	activity_counts = pd.DataFrame.from_dict(activity_counts)
	st.bar_chart(activity_counts.transpose())

with st.echo():
	# Show the pie chart on the page
	data_ = data.dropna(subset=['Activity Evidence'])
	pie_chart = {}
	for region in regions:
		pie_chart[region] = len(data[data['Region'] == region])
	
	labels = list(pie_chart.keys())
	counts = list(pie_chart.values())

	fig, ax = plt.subplots(figsize=(15,15))
	ax.pie(counts, labels=labels, autopct='%1.1f%%', shadow=False, startangle=90)
	fig.tight_layout()
	st.pyplot(fig)

with st.echo():
	# Create a stacked bar chart showing average elevation:
	data_ = data.dropna(subset=['Elevation'])
	regions = data_['Region'].unique()

	elevation_means = {}

	for region in regions:
		region_data = data_[data_['Region'] == region]['Elevation']
		elevation_means[region] = {region : np.mean(np.array(region_data))}
	
	elevation_means = pd.DataFrame.from_dict(elevation_means)
	st.bar_chart(elevation_means.transpose())

with st.echo():
	# Create a histogram showing the distribution of elevations
	fig, ax = plt.subplots(figsize=(15,15))
	ax.hist(data['Elevation'])
	st.pyplot(fig)


# Add a footer with contact information
# Borrowed footer code:
footer="""<style>
a:link , a:visited{
color: blue;
background-color: transparent;
text-decoration: underline;
}

a:hover,  a:active {
color: red;
background-color: transparent;
text-decoration: underline;
}

.footer {
position: fixed;
left: 0;
bottom: 0;
width: 100%;
background-color: white;
color: black;
text-align: center;
}
</style>
<div class="footer">
<p>Contact us at <a style='display: block; text-align: center;' href="info@volcano-data.com" target="_blank">info@volcano-data.com</a></p>
</div>
"""
st.markdown(footer,unsafe_allow_html=True)