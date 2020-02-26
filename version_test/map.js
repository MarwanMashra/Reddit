$(document).ready(function(){
			var data= {
				"TotalResults": 113, 	
				"Results": [
					{"lng": "1.604", "lat": "43.71553", "img": "https://i.redd.it/dc57tyoiwqf41.jpg", "url": "https://www.reddit.com/r/EarthPorn/comments/f9azm5/the_most_beautiful_canyon_in_the_world_south/"}, 
					{"lng": "7.07897", "lat": "43.56992", "img": "https://i.redd.it/2qhzpuf77se41.jpg", "url": "https://www.reddit.com/r/EarthPorn/comments/f93lfw/its_the_sunsets_you_never_expect_to_be_great_that/"}, 
					{"lng": "-0.14591", "lat": "42.77424", "img": "https://i.redd.it/82qludd2ywd41.jpg", "url": "https://www.reddit.com/r/EarthPorn/comments/f9h8k6/a_cloudy_sunrise_sipping_coffee_in_banff_moraine/"},
					{"lng": "2.3488", "lat": "48.85341", "img": "https://i.redd.it/djk6zusqtud41.jpg", "url": "https://www.reddit.com/r/EarthPorn/comments/f9gh14/aerial_image_of_a_ground_fed_river_central_oregon/"}, 
					{"lng": "-3.11963", "lat": "47.48412", "img": "https://i.redd.it/fel901lhnzc41.jpg", "url": "https://www.reddit.com/r/EarthPorn/comments/f9j12t/super_moody_scenes_of_el_capitan_with_the_morning/"}, 
					{"lng": "-1.05283", "lat": "43.72566", "img": "https://i.redd.it/41ww8wwivrc41.jpg", "url": "https://www.reddit.com/r/EarthPorn/comments/f9dfsn/zion_np_utah_the_narrows_in_february_3024x4032_oc/"}
					]
			}

			var mymap = L.map('mapid').setView([ 47,  2], 5);                                 //position dans la map
			L.tileLayer('http://{s}.google.com/vt/lyrs=s,h&x={x}&y={y}&z={z}',{
    		maxZoom: 20,
    		subdomains:['mt0','mt1','mt2','mt3']
			}).addTo(mymap);


			$.each(data['Results'],function(i){

					var html= '<div id="container'+i+'" class="container"><img id="image'+i+'" class="image" src="'+data['Results'][i]['img']+'"></div>';

					var myIcon = L.icon({
						iconUrl: data['Results'][i]['img'],
						iconSize: ['auto', 45]
						
					});


					var marker = L.marker( 
						[ data['Results'][i]['lat'] , data['Results'][i]['lng'] ], 
						{icon: myIcon}).addTo(mymap).bindPopup('<iframe id="iframeReddit" style="top: 160px; left: 0px;" src='+data["Results"][i]["url"]+'></iframe>').openPopup();
				});
		});


