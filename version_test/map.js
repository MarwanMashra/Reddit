$(document).ready(function(){

	//data avec bcp d'images
	//data = {"head": {"total": 21, "country": {"name": "France", "lng": "2", "lat": "46"}}, "results": [{"lng": "2.3499", "lat": "48.8709", "img": "https://i.redd.it/7h95m06db2w31.png", "url": "https://www.reddit.com/r/EarthPorn/comments/dq33cp/i_woke_up_at_430_am_hiked_up_for_2_hrs_and_saw/", "date": {"year": 2019, "month": 11, "day": 1, "hour": 11, "min": 44, "sec": 13}, "author": {"name": "dwd0tcom", "icon": "https://styles.redditmedia.com/t5_d9jre/styles/profileIcon_h994xh4vf9g31.jpg?width=256&height=256&crop=256:256,smart&s=d8bf8b24961489d2401c45a3df5eddd915487a1f", "profile": "https://www.reddit.com/user/dwd0tcom"}}, {"lng": "2.3499", "lat": "48.8709", "img": "https://i.redd.it/ldo1mxojjug41.jpg", "url": "https://www.reddit.com/r/EarthPorn/comments/f3p3c0/sunrise_chamonix_france_oc_1080x1080_ig/", "date": {"year": 2020, "month": 2, "day": 14, "hour": 8, "min": 2, "sec": 23}, "author": {"name": "dwd0tcom", "icon": "https://styles.redditmedia.com/t5_d9jre/styles/profileIcon_h994xh4vf9g31.jpg?width=256&height=256&crop=256:256,smart&s=d8bf8b24961489d2401c45a3df5eddd915487a1f", "profile": "https://www.reddit.com/user/dwd0tcom"}}, {"lng": "2.3499", "lat": "48.8709", "img": "https://i.redd.it/6xoecfbkkwh41.jpg", "url": "https://www.reddit.com/r/EarthPorn/comments/f6cmwv/my_view_from_atop_aiguille_du_midi_in_chamonix/", "date": {"year": 2020, "month": 2, "day": 19, "hour": 15, "min": 55, "sec": 50}, "author": {"name": "hungbandit007", "icon": "https://styles.redditmedia.com/t5_eaxo0/styles/profileIcon_01k7755i1zl11.jpg?width=256&height=256&crop=256:256,smart&s=149535bd640c387abe8640a367d8e7533df20af2", "profile": "https://www.reddit.com/user/hungbandit007"}}, {"lng": "6.92463", "lat": "45.49604", "img": "https://i.redd.it/fpply17d7dh41.jpg", "url": "https://www.reddit.com/r/EarthPorn/comments/f4yq5v/tignes_lake_in_france_behind_the_frozen_trees/", "date": {"year": 2020, "month": 2, "day": 16, "hour": 22, "min": 48, "sec": 14}, "author": {"name": "ArtGirlWithGlasses", "icon": "https://www.redditstatic.com/avatars/avatar_default_03_FF66AC.png", "profile": "https://www.reddit.com/user/ArtGirlWithGlasses"}}, {"lng": "9.50963", "lat": "42.10215", "img": "https://i.redd.it/1pog0edg4qk41.jpg", "url": "https://www.reddit.com/r/EarthPorn/comments/fdk3o7/porto_bay_corsica_france_oc_4476x3357/", "date": {"year": 2020, "month": 3, "day": 4, "hour": 21, "min": 28, "sec": 35}, "author": {"name": "Haruspex1984", "icon": "https://www.redditstatic.com/avatars/avatar_default_16_D4E815.png", "profile": "https://www.reddit.com/user/Haruspex1984"}}, {"lng": "5.44334", "lat": "43.20741", "img": "https://i.redd.it/2qhzpuf77se41.jpg", "url": "https://www.reddit.com/r/EarthPorn/comments/eyewe1/secret_paradise_in_france_not_so_secret_after_9/", "date": {"year": 2020, "month": 2, "day": 3, "hour": 22, "min": 3, "sec": 27}, "author": {"name": "GungieBum", "icon": "https://www.redditstatic.com/avatars/avatar_default_13_EA0027.png", "profile": "https://www.reddit.com/user/GungieBum"}}, {"lng": "6.5918", "lat": "43.2332", "img": "https://i.redd.it/l4tv4oyjgqi41.jpg", "url": "https://www.reddit.com/r/EarthPorn/comments/f8faar/montgenevre_french_alps_on_the_border_franceitaly/", "date": {"year": 2020, "month": 2, "day": 23, "hour": 20, "min": 27, "sec": 16}, "author": {"name": "chicodetolosa", "icon": "https://www.redditstatic.com/avatars/avatar_default_06_46D160.png", "profile": "https://www.reddit.com/user/chicodetolosa"}}, {"lng": "10", "lat": "46.41667", "img": "https://i.redd.it/8mjakr1mbbi41.jpg", "url": "https://www.reddit.com/r/EarthPorn/comments/f7ehud/sunset_behind_a_mountain_in_chamroussealpsfrance/", "date": {"year": 2020, "month": 2, "day": 21, "hour": 17, "min": 32, "sec": 21}, "author": {"name": "Necooooooo", "icon": "https://styles.redditmedia.com/t5_2a39co/styles/profileIcon_8oq0f5xy4o341.jpeg?width=256&height=256&crop=256:256,smart&s=8828c6480d8a74585cf2cf3c49f0584e829cc614", "profile": "https://www.reddit.com/user/Necooooooo"}}, {"lng": "1.09932", "lat": "49.44313", "img": "https://i.redd.it/12ihwozm8dk31.jpg", "url": "https://www.reddit.com/r/EarthPorn/comments/cz3prb/a_dramatic_change_of_weather_on_the_beach/", "date": {"year": 2019, "month": 9, "day": 3, "hour": 11, "min": 41, "sec": 52}, "author": {"name": "Ron_Jansen", "icon": "https://www.redditstatic.com/avatars/avatar_default_07_C18D42.png", "profile": "https://www.reddit.com/user/Ron_Jansen"}}, {"lng": "2.3499", "lat": "48.8709", "img": "https://i.redd.it/6wbjlunbdlc41.jpg", "url": "https://www.reddit.com/r/EarthPorn/comments/eszbhp/view_of_aiguille_du_midi_while_climbing_mont/", "date": {"year": 2020, "month": 1, "day": 23, "hour": 20, "min": 58, "sec": 7}, "author": {"name": "neaturmanmike", "icon": "https://styles.redditmedia.com/t5_29hgj6/styles/profileIcon_l4kbxmjici241.jpg?width=256&height=256&crop=256:256,smart&s=ed853e72636730caf88fa761eae105629a95f2db", "profile": "https://www.reddit.com/user/neaturmanmike"}}, {"lng": "4.193", "lat": "49.63606", "img": "https://i.redd.it/9n2k7oq4f6941.jpg", "url": "https://www.reddit.com/r/EarthPorn/comments/ekvjqp/forest_fog_france_oc_3072x6080/", "date": {"year": 2020, "month": 1, "day": 6, "hour": 15, "min": 26, "sec": 30}, "author": {"name": "peter-bone", "icon": "https://www.redditstatic.com/avatars/avatar_default_02_25B79F.png", "profile": "https://www.reddit.com/user/peter-bone"}}, {"lng": "8.73812", "lat": "41.91886", "img": "https://i.redd.it/ybqz3es9fe541.jpg", "url": "https://www.reddit.com/r/EarthPorn/comments/ecd1gv/gorges_du_verdon_south_of_france_oc_4032_x_3024/", "date": {"year": 2019, "month": 12, "day": 18, "hour": 14, "min": 4, "sec": 45}, "author": {"name": "princessofmeowtown_", "icon": "https://www.redditstatic.com/avatars/avatar_default_12_46D160.png", "profile": "https://www.reddit.com/user/princessofmeowtown_"}}, {"lng": "6.23775", "lat": "46.19439", "img": "https://i.redd.it/pguqv9z6wbw31.jpg", "url": "https://www.reddit.com/r/EarthPorn/comments/dqpjta/early_morning_mists_filling_the_vall\u00e9e_daulps/", "date": {"year": 2019, "month": 11, "day": 2, "hour": 20, "min": 1, "sec": 47}, "author": {"name": "Alpinekiwi", "icon": "https://www.redditstatic.com/avatars/avatar_default_03_0079D3.png", "profile": "https://www.reddit.com/user/Alpinekiwi"}}, {"lng": "1.604", "lat": "43.71553", "img": "https://i.redd.it/dc57tyoiwqf41.jpg", "url": "https://www.reddit.com/r/EarthPorn/comments/f0vqqm/biking_through_the_bogs_of_les_camargues_southern/", "date": {"year": 2020, "month": 2, "day": 8, "hour": 18, "min": 44, "sec": 38}, "author": {"name": "phaexal", "icon": "https://www.redditstatic.com/avatars/avatar_default_04_545452.png", "profile": "https://www.reddit.com/user/phaexal"}}, {"lng": "5.83333", "lat": "45.16667", "img": "https://i.redd.it/mv13wbg5gz741.jpg", "url": "https://www.reddit.com/r/EarthPorn/comments/ei3usr/foggy_forest_in_france_is\u00e8re_4000x6000oc/", "date": {"year": 2019, "month": 12, "day": 31, "hour": 14, "min": 57, "sec": 36}, "author": {"name": "Gladeryn", "icon": "https://www.redditstatic.com/avatars/avatar_default_16_46D160.png", "profile": "https://www.reddit.com/user/Gladeryn"}}, {"lng": "6.864", "lat": "45.833", "img": "https://i.redd.it/fwvz8bg7rma41.jpg", "url": "https://www.reddit.com/r/EarthPorn/comments/eocdfv/view_from_the_mont_blanc_france_3800m_oc_5738x3228/", "date": {"year": 2020, "month": 1, "day": 13, "hour": 23, "min": 26, "sec": 24}, "author": {"name": "world_live", "icon": "https://www.redditstatic.com/avatars/avatar_default_08_EA0027.png", "profile": "https://www.reddit.com/user/world_live"}}, {"lng": "-0.13333", "lat": "42.78333", "img": "https://i.redd.it/82qludd2ywd41.jpg", "url": "https://www.reddit.com/r/EarthPorn/comments/ew50xn/view_from_the_top_of_grand_vignemale_france/", "date": {"year": 2020, "month": 1, "day": 30, "hour": 12, "min": 56, "sec": 30}, "author": {"name": "Waltonr", "icon": "https://www.redditstatic.com/avatars/avatar_default_15_D4E815.png", "profile": "https://www.reddit.com/user/Waltonr"}}, {"lng": "5.44973", "lat": "43.5283", "img": "https://i.redd.it/nw9bvgoqise41.jpg", "url": "https://www.reddit.com/r/EarthPorn/comments/eyfvtz/mount_stvictoire_from_the_path_to_refuge_c\u00e9zanne/", "date": {"year": 2020, "month": 2, "day": 3, "hour": 23, "min": 6, "sec": 21}, "author": {"name": "xenosthemutant", "icon": "https://www.redditstatic.com/avatars/avatar_default_01_FF585B.png", "profile": "https://www.reddit.com/user/xenosthemutant"}}, {"lng": "10", "lat": "46.41667", "img": "https://imgur.com/L1SmRJN", "url": "https://www.reddit.com/r/EarthPorn/comments/eri2kt/the_alps_france_oc_4032x3024/", "date": {"year": 2020, "month": 1, "day": 20, "hour": 19, "min": 21, "sec": 22}, "author": {"name": "superzamp", "icon": "https://www.redditstatic.com/avatars/avatar_default_18_FFD635.png", "profile": "https://www.reddit.com/user/superzamp"}}, {"lng": "10", "lat": "46.41667", "img": "https://i.redd.it/drrwiaoz3e841.jpg", "url": "https://www.reddit.com/r/EarthPorn/comments/ej07um/lake_laramon_under_a_starry_night_sky_the_alps/", "date": {"year": 2020, "month": 1, "day": 2, "hour": 16, "min": 17, "sec": 24}, "author": {"name": "Gladeryn", "icon": "https://www.redditstatic.com/avatars/avatar_default_16_46D160.png", "profile": "https://www.reddit.com/user/Gladeryn"}}, {"lng": "6.84829", "lat": "45.55183", "img": "https://i.redd.it/41ww8wwivrc41.jpg", "url": "https://www.reddit.com/r/EarthPorn/comments/eteq8w/mont_pourri_view_from_aiguille_rouge_france/", "date": {"year": 2020, "month": 1, "day": 24, "hour": 18, "min": 52, "sec": 16}, "author": {"name": "phalacracorax", "icon": "https://www.redditstatic.com/avatars/avatar_default_14_0079D3.png", "profile": "https://www.reddit.com/user/phalacracorax"}}]}

	//data avec moins d'images mais plus rapide 
	data =  {"head": {"total": 21, "country": {"name": "France", "lng": "2", "lat": "46"}}, "results": [{"lng": "2.3499", "lat": "48.8709", "img": "https://i.redd.it/6xoecfbkkwh41.jpg", "url": "https://www.reddit.com/r/EarthPorn/comments/f6cmwv/my_view_from_atop_aiguille_du_midi_in_chamonix/", "date": {"year": 2020, "month": 2, "day": 19, "hour": 15, "min": 55, "sec": 50}, "author": {"name": "hungbandit007", "icon": "https://styles.redditmedia.com/t5_eaxo0/styles/profileIcon_01k7755i1zl11.jpg?width=256&height=256&crop=256:256,smart&s=149535bd640c387abe8640a367d8e7533df20af2", "profile": "https://www.reddit.com/user/hungbandit007"}},{"lng": "10", "lat": "46.41667", "img": "https://i.redd.it/drrwiaoz3e841.jpg", "url": "https://www.reddit.com/r/EarthPorn/comments/ej07um/lake_laramon_under_a_starry_night_sky_the_alps/", "date": {"year": 2020, "month": 1, "day": 2, "hour": 16, "min": 17, "sec": 24}, "author": {"name": "Gladeryn", "icon": "https://www.redditstatic.com/avatars/avatar_default_16_46D160.png", "profile": "https://www.reddit.com/user/Gladeryn"}}, {"lng": "6.84829", "lat": "45.55183", "img": "https://i.redd.it/41ww8wwivrc41.jpg", "url": "https://www.reddit.com/r/EarthPorn/comments/eteq8w/mont_pourri_view_from_aiguille_rouge_france/", "date": {"year": 2020, "month": 1, "day": 24, "hour": 18, "min": 52, "sec": 16}, "author": {"name": "phalacracorax", "icon": "https://www.redditstatic.com/avatars/avatar_default_14_0079D3.png", "profile": "https://www.reddit.com/user/phalacracorax"}}]}
	//création de la carte
	var mymap = L.map('mapid');                 
	L.tileLayer('http://{s}.google.com/vt/lyrs=s,h&x={x}&y={y}&z={z}',{
    		maxZoom: 20,
    		subdomains:['mt0','mt1','mt2','mt3']
			}).addTo(mymap);


	  
	//se placer sur la carte
	mymap.setView([ data['head']['country']['lat'],  data['head']['country']['lng']], 5);                                
	//placer les images
	$.each(data['results'],function(i){
		var myIcon = L.icon({
			iconUrl:data['results'][i]['img'],
			iconSize: [60,40]
		});
		L.marker( [ data['results'][i]['lat'] , data['results'][i]['lng'] ],{icon: myIcon}).addTo(mymap);
	});
	 

	// affichage des images quand on les clique 
	$(".leaflet-marker-pane > img").click(function(){                      // quand on clique sur une image sur la carte
		var src = $(this).attr('src');                                     // chercher l'url de l'image 
		var index = data['results'].findIndex(x => x.img == src);          // chercher l'index de l'image dans la liste des images
		var image = data['results'][index];                                // récupérer l'image comme un dictionnaire 

		/*
			image['lng'] nous donne la longitude
			image['alt'] nous donne la laltitude 
			image['img'] nous donne l'url de l'image 
			image['url'] nous donne l'url de la post (la publication sur reddit)
			image['date'] nous donne la date de l'image tel que:
				image['date']['year']   nous donne l'année 
				image['date']['month']  nous donne le mois 
				image['date']['day']    nous donne le jour du mois
				image['date']['hour']   nous donne l'heure
				image['date']['min']    nous donne la minute 
				image['date']['sec']    nous donne la seconde 
			image['author'] nous donne des informations sur l'author tel que:
				image['author']['name']       nous donne son nom
				image['author']['icon']       nous donne sa photo de profils
				image['author']['profile']    nous donne l'url vers son profile

		*/


		//affichage de l'image
		alert("vous avez cliquer sur l'image "+index);







	});
	

});






