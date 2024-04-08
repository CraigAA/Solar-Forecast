Site="38c7-5747-151e-b77e" # Angaston location key
http="https://api.solcast.com.au/weather_sites/" + Site + "/forecasts?format=json&api_key=" + APIKey
weather_json = system.net.httpGet(http)
weather_json_decoded = system.util.jsonDecode(weather_json)

path='[default]Weather/Solar/'
count =int(0)
hour_forecast=[]

for hour in weather_json_decoded["forecasts"]: #Pick the right data and store
	if (count % 2)==0:#Only use hourly data not 30 minute data'
#		print hour
		#First get date in to right format and timezone
		dateInput=hour['period_end']
		dateInput = dateInput.replace('T', " ")
		dateInput=system.date.parse(dateInput,'yyyy-MM-dd HH:mm:ss')
		dateInput=system.date.addMinutes(dateInput,(9*60+30)) #ACST = +9:30 UTC
		hour_forecast.append([dateInput,hour["air_temp"],hour['ghi']])
		q='select * from solar_forecast where forecast_time = ?' 
		existing=system.db.runPrepQuery(q, [dateInput],'nas_development')
		if len(existing)!=0:
			q='update solar_forecast set ghi=?,ebh=?,dni=?,cloud_opacity=?, t_stamp=CURRENT_TIMESTAMP where forecast_time=?'
			system.db.runPrepUpdate(q,[hour['ghi'],hour['ebh'],hour['dni'],hour['cloud_opacity']/10,dateInput],'nas_development')
			print 'update forecast '+str(dateInput)
		q='insert into solar_forecast (forecast_time, ghi,ebh,dni,cloud_opacity) values (?,?,?,?,?)'
		system.db.runPrepUpdate(q, [dateInput , hour['ghi'],hour['ebh'],hour['dni'],hour['cloud_opacity']/10],'nas_development')
	count+=1
		
hour_forecast=system.dataset.toDataSet(['Time','Temperature', 'Solar'],hour_forecast)
system.tag.write(path+'Weather_Data_7Days/Weather_Data',hour_forecast)
system.tag.write(path+'Weather_Data_7Days/Last_Weather_Forecast_Update',system.date.now())

# record current temperature
system.tag.write(path+'Air_Temp', hour_forecast.getValueAt(0, 'Temperature'))

# record hourly temps
for i in range(24 - system.date.getHour24(hour_forecast.getValueAt(0, 'Time')) + 1): #Organise the data
	hour = system.date.getHour24(hour_forecast.getValueAt(0, 'Time')) + i
#	tag_path = 'Weather_Data_7Days/Air_Temp/' + str(hour)
#	if system.tag.exists(tag_path):
#		system.tag.write(tag_path,hour_forecast.getValueAt(i, 'Temperature'))
	tag_path = path+'Weather_Data_7Days/Hour/'+str(hour)
	if system.tag.exists(tag_path):
		system.tag.write(tag_path,hour_forecast.getValueAt(i, 'Solar'))
