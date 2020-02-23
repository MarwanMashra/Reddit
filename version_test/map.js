$(document).ready(function(){
			var data= {
				"TotalResults": 113, 	
				"Results": [
					{"lng": "1.604", "lat": "43.71553", "img": "https://i.redd.it/dc57tyoiwqf41.jpg"}, 
					{"lng": "7.07897", "lat": "43.56992", "img": "https://i.redd.it/2qhzpuf77se41.jpg"}, 
					{"lng": "-0.14591", "lat": "42.77424", "img": "https://i.redd.it/82qludd2ywd41.jpg"},
					{"lng": "2.3488", "lat": "48.85341", "img": "https://i.redd.it/djk6zusqtud41.jpg"}, 
					{"lng": "-3.11963", "lat": "47.48412", "img": "https://i.redd.it/fel901lhnzc41.jpg"}, 
					{"lng": "-1.05283", "lat": "43.72566", "img": "https://i.redd.it/41ww8wwivrc41.jpg"}, 
					{"lng": "6.86933", "lat": "45.92375", "img": "https://i.redd.it/6wbjlunbdlc41.jpg"}, 
					{"lng": "1.604", "lat": "43.71553", "img": "https://i.redd.it/x2voqzy0b1c41.jpg"}, 
					{"lng": "5.38107", "lat": "43.29695", "img": "https://imgur.com/L1SmRJN"}, 
					{"lng": "7.09529", "lat": "47.91297", "img": "https://i.redd.it/rr2xs543b6b41.jpg"}, 
					{"lng": "0.48171", "lat": "44.85157", "img": "https://i.redd.it/o2c8b28nc5b41.jpg"}, 
					{"lng": "6.87787", "lat": "48.07346", "img": "https://i.redd.it/ulx7s3m5y4b41.jpg"}, 
					{"lng": "2.96408", "lat": "45.77252", "img": "https://i.redd.it/nit1ulse43b41.jpg"},
					{"lng": "6.87787", "lat": "48.07346", "img": "https://i.redd.it/ulx7s3m5y4b41.jpg"}, 
					{"lng": "2.96408", "lat": "45.77252", "img": "https://i.redd.it/nit1ulse43b41.jpg"}
				]
			}

			var mymap = L.map('mapid').setView([ 47,  2], 5);                                 //position dans la map
			L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {               //url map + zoom
    		attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
			}).addTo(mymap);


			$.each(data['Results'],function(i){
				var html= '<div id="container'+i+'" class="container"><img id="image'+i+'" class="image" src="'+data['Results'][i]['img']+'"></div>';

					var marker = L.marker( [ data['Results'][i]['lat'] , data['Results'][i]['lng'] ]).addTo(mymap).bindPopup(html).openPopup();

			});

});
