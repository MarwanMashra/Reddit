$(document).ready(function(){

	//variable globale
	var search_version;
	var session;
	var reported_images=[];
	var est_admin;
	var is_scraping=false;

	//si vous êtes en train de tester, mettez le à true, vous serez pas obligez à lancer une recherche à chaque fois
	var DEBUG=false;
	var admin=false;
	//création de la carte
	var mymap = L.map('mapid');                 
	L.tileLayer('http://{s}.google.com/vt/lyrs=s,h&x={x}&y={y}&z={z}',{
    		maxZoom: 20,
    		subdomains:['mt0','mt1','mt2','mt3']
			}).addTo(mymap);
	mymap.setView([ 46,  2], 6);
	if(DEBUG){
		data = {"head":{"country":{"lat":"46","lng":"2","name":"France"},"total":49},"results":[{"author":{"icon":"https://www.redditstatic.com/avatars/avatar_default_19_94E044.png","name":"aleksw","profile":"https://www.reddit.com/user/aleksw"},"date":{"day":26,"hour":8,"min":21,"month":3,"sec":9,"year":2020},"img_url":"https://i.redd.it/nuhmmic48zo41.jpg","lat":"44.25","lng":"-1","name":"The Landes","search_version":"1.00","text":"Kayaking in Les gorges de l'ard\u00e8che in south of France [1824x3648] [OC]","url":"https://www.reddit.com/r/EarthPorn/comments/fp7vh0/kayaking_in_les_gorges_de_lard\u00e8che_in_south_of/"},{"author":{"icon":"https://www.redditstatic.com/avatars/avatar_default_02_D4E815.png","name":"zanpetto","profile":"https://www.reddit.com/user/zanpetto"},"date":{"day":16,"hour":7,"min":37,"month":4,"sec":53,"year":2020},"img_url":"https://i.redd.it/oh3kxktov4t41.jpg","lat":"47.16667","lng":"7","name":"Jura","search_version":"1.00","text":"Fresh morning 3 chateaux Jura France,[OC], [4032x2268]","url":"https://www.reddit.com/r/EarthPorn/comments/g2ag8l/fresh_morning_3_chateaux_jura_franceoc_4032x2268/"},{"author":{"icon":"https://styles.redditmedia.com/t5_etbys/styles/profileIcon_8dfywjf0qqi41.png?width=256&height=256&crop=256:256,smart&s=cd2ebaa69e8d62e314a24f3a810c7a98449304b2","name":"Ablakor","profile":"https://www.reddit.com/user/Ablakor"},"date":{"day":28,"hour":10,"min":47,"month":3,"sec":45,"year":2020},"img_url":"https://i.redd.it/lx1937p18ep41.jpg","lat":"45.45142","lng":"6.97455","name":"Val d'Is\u00e8re","search_version":"1.00","text":"The amazing view from one of my favourite ski resorts in France. Val d'Is\u00e8re, France. [OC] [2016x980]","url":"https://www.reddit.com/r/EarthPorn/comments/fqhvz4/the_amazing_view_from_one_of_my_favourite_ski/"},{"author":{"icon":"https://styles.redditmedia.com/t5_d9jre/styles/profileIcon_h994xh4vf9g31.jpg?width=256&height=256&crop=256:256,smart&s=d8bf8b24961489d2401c45a3df5eddd915487a1f","name":"dwd0tcom","profile":"https://www.reddit.com/user/dwd0tcom"},"date":{"day":1,"hour":11,"min":44,"month":11,"sec":13,"year":2019},"img_url":"https://i.redd.it/7h95m06db2w31.png","lat":"45.92375","lng":"6.86933","name":"Chamonix","search_version":"1.00","text":"I woke up at 4:30 AM, hiked up for 2 hrs and saw this incredible show. Chamonix, France. [OC][1080x1080] Instagram: @bavarianexplorer","url":"https://www.reddit.com/r/EarthPorn/comments/dq33cp/i_woke_up_at_430_am_hiked_up_for_2_hrs_and_saw/"},{"author":{"icon":"https://styles.redditmedia.com/t5_2eez0s/styles/profileIcon_51h7eun2f6t41.jpg?width=256&height=256&crop=256:256,smart&s=ee2479b4d334ce9120ffa7c872b60f2eba5fd0ea","name":"tegucigalpa1337","profile":"https://www.reddit.com/user/tegucigalpa1337"},"date":{"day":29,"hour":21,"min":50,"month":3,"sec":45,"year":2020},"img_url":"https://i.redd.it/dbxaohz6nop41.jpg","lat":"42.04062","lng":"9.0136","name":"Corsica","search_version":"1.00","text":"Wind shaped tree, Corsica, France [OC] [2667x2000]","url":"https://www.reddit.com/r/EarthPorn/comments/fre2rn/wind_shaped_tree_corsica_france_oc_2667x2000/"},{"author":{"icon":"https://www.redditstatic.com/avatars/avatar_default_11_94E044.png","name":"Eggseater","profile":"https://www.reddit.com/user/Eggseater"},"date":{"day":19,"hour":15,"min":35,"month":4,"sec":35,"year":2020},"img_url":"https://i.redd.it/7qbmehmhnst41.jpg","lat":"46","lng":"2","name":"France","search_version":"1.00","text":"Lonesome tree on our road trip through France. [5970x3980] OC","url":"https://www.reddit.com/r/EarthPorn/comments/g49mht/lonesome_tree_on_our_road_trip_through_france/"},{"author":{"icon":"https://www.redditstatic.com/avatars/avatar_default_04_DDBD37.png","name":"lcntzn","profile":"https://www.reddit.com/user/lcntzn"},"date":{"day":17,"hour":21,"min":38,"month":4,"sec":56,"year":2020},"img_url":"https://i.redd.it/8ci8ckin6gt41.jpg","lat":"46.13199","lng":"1.15767","name":"Ardent","search_version":"1.00","text":"Ardent, Montriond, Haute Savoie, France [1346x2951] [OC]","url":"https://www.reddit.com/r/EarthPorn/comments/g3b418/ardent_montriond_haute_savoie_france_1346x2951_oc/"},{"author":{"icon":"https://www.redditstatic.com/avatars/avatar_default_03_0079D3.png","name":"Alpinekiwi","profile":"https://www.reddit.com/user/Alpinekiwi"},"date":{"day":14,"hour":10,"min":44,"month":4,"sec":7,"year":2020},"img_url":"https://i.redd.it/p17dwmloirs41.jpg","lat":"46.1827","lng":"6.6426","name":"Roc d'Enfer","search_version":"1.00","text":"Missing climbing local peaks. Roc d'Enfer, Haute Savoie, France. (5632 \u00d7 2910) [OC]","url":"https://www.reddit.com/r/EarthPorn/comments/g13aif/missing_climbing_local_peaks_roc_denfer_haute/"},{"author":{"icon":"https://www.redditstatic.com/avatars/avatar_default_03_FF585B.png","name":"NaClMux","profile":"https://www.reddit.com/user/NaClMux"},"date":{"day":12,"hour":15,"min":50,"month":4,"sec":14,"year":2020},"img_url":"https://i.redd.it/70t4j6xvres41.jpg","lat":"45.5","lng":"5.33333","name":"Rh\u00f4ne-Alpes","search_version":"1.00","text":"Over a waterfall, Rh\u00f4ne-Alpes, France. [2048x1536] [OC]","url":"https://www.reddit.com/r/EarthPorn/comments/fzz1ww/over_a_waterfall_rh\u00f4nealpes_france_2048x1536_oc/"},{"author":{"icon":"https://www.redditstatic.com/avatars/avatar_default_06_FFD635.png","name":"dagnyroark19","profile":"https://www.reddit.com/user/dagnyroark19"},"date":{"day":18,"hour":4,"min":57,"month":4,"sec":47,"year":2020},"img_url":"https://i.redd.it/fdj8t95ycit41.jpg","lat":"44.13806","lng":"4.81025","name":"Orange","search_version":"1.00","text":"Orange glows at Eze beach, France. (3000\u00d73750) [OC]","url":"https://www.reddit.com/r/EarthPorn/comments/g3hw7u/orange_glows_at_eze_beach_france_30003750_oc/"},{"author":{"icon":"https://www.redditstatic.com/avatars/avatar_default_14_94E044.png","name":"Musopia123","profile":"https://www.reddit.com/user/Musopia123"},"date":{"day":25,"hour":10,"min":31,"month":3,"sec":56,"year":2020},"img_url":"https://i.redd.it/dkznmjwoqso41.jpg","lat":"50.9264","lng":"1.7091","name":"Cap Blanc-Nez","search_version":"1.00","text":"Emptiness..... Cap Blanc Nez, pas de Calais, France. [4608x3456] [OC]","url":"https://www.reddit.com/r/EarthPorn/comments/foo2kw/emptiness_cap_blanc_nez_pas_de_calais_france/"},{"author":{"icon":"https://www.redditstatic.com/avatars/avatar_default_05_C18D42.png","name":"Tygerpanther","profile":"https://www.reddit.com/user/Tygerpanther"},"date":{"day":7,"hour":13,"min":0,"month":3,"sec":43,"year":2020},"img_url":"https://i.imgur.com/yIXWXCs.jpg","lat":"45.08034","lng":"2.70663","name":"Puy Griou","search_version":"1.00","text":"Sight from the Puy Marie, France - on the right, the grey Puy Griou is one of the remains of an ancient supervolcano from 6 million years ago [OC] [3416x2873]","url":"https://www.reddit.com/r/EarthPorn/comments/feutse/sight_from_the_puy_marie_france_on_the_right_the/"},{"author":{"icon":"https://styles.redditmedia.com/t5_5evqw/styles/profileIcon_7xnlpbyrkls41.jpg?width=256&height=256&crop=256:256,smart&s=106ad24acfb02a5318733d8df7989da0de36c6eb","name":"tapyr","profile":"https://www.reddit.com/user/tapyr"},"date":{"day":13,"hour":15,"min":13,"month":4,"sec":32,"year":2020},"img_url":"https://imgur.com/CNN11Iz","lat":"48.78523","lng":"2.57864","name":"Ambiance Hotel","search_version":"1.00","text":"Ancient Ambiance on the Corbi\u00e8res Massif, Southwest France, [6016 x 4000] [OC]","url":"https://www.reddit.com/r/EarthPorn/comments/g0ktog/ancient_ambiance_on_the_corbi\u00e8res_massif/"},{"author":{"icon":"https://styles.redditmedia.com/t5_d9jre/styles/profileIcon_h994xh4vf9g31.jpg?width=256&height=256&crop=256:256,smart&s=d8bf8b24961489d2401c45a3df5eddd915487a1f","name":"dwd0tcom","profile":"https://www.reddit.com/user/dwd0tcom"},"date":{"day":14,"hour":8,"min":2,"month":2,"sec":23,"year":2020},"img_url":"https://i.redd.it/ldo1mxojjug41.jpg","lat":"45.92375","lng":"6.86933","name":"Chamonix","search_version":"1.00","text":"Sunrise. Chamonix, France. OC [1080x1080] IG: @bavarianexplorer","url":"https://www.reddit.com/r/EarthPorn/comments/f3p3c0/sunrise_chamonix_france_oc_1080x1080_ig/"},{"author":{"icon":"https://www.redditstatic.com/avatars/avatar_default_06_D4E815.png","name":"alkophoto","profile":"https://www.reddit.com/user/alkophoto"},"date":{"day":5,"hour":17,"min":19,"month":4,"sec":44,"year":2020},"img_url":"https://i.redd.it/to796j7e91r41.jpg","lat":"43.70303","lng":"7.24862","name":"du midi","search_version":"1.00","text":"Aiguille du Midi - Mont Blanc, France [OC] [1814 \u00d7 1053]","url":"https://www.reddit.com/r/EarthPorn/comments/fvhe7p/aiguille_du_midi_mont_blanc_france_oc_1814_1053/"},{"author":{"icon":"https://styles.redditmedia.com/t5_u6rvj/styles/profileIcon_gvjhdze0fv821.jpg?width=256&height=256&crop=256:256,smart&s=5a6556fc9ae03492e2efbfdc585e737856943e45","name":"mpmark","profile":"https://www.reddit.com/user/mpmark"},"date":{"day":7,"hour":8,"min":24,"month":4,"sec":45,"year":2020},"img_url":"https://i.redd.it/6gds95iuvcr41.jpg","lat":"46.13607","lng":"6.47829","name":"Pont du Giffre","search_version":"1.00","text":"The play of light and shadow on the walls of the magnificent U-valley of Giffre in Sixt-Fer-\u00e0-Cheval Nature Reserve in southeastern France on an early autumn morning 19/10/2013 [OC] [1413x2048] @mpxmark","url":"https://www.reddit.com/r/EarthPorn/comments/fwgtjs/the_play_of_light_and_shadow_on_the_walls_of_the/"}]};
		//data = {"head":{"country":{"lat":"46","lng":"2","name":"France"},"total":49},"results":[]};
		createMap(data);
	}

	//récupérer les informations de la session
	$.ajax({
		type:"GET",
		url:"/get_session",
		success: createElementsUSer
	}).fail(printError); 
	
	//requête get_list_version
	$.ajax({
		type:"GET",
		url:"/get_list_version",
		success: createVerionSelector 
	}).fail(printError);  
	

	function createElementsUSer(x){
		session = x;
		est_admin = session['admin?'];
		if(session['username']){//<a href="{{ url_for('map') }}"><button id="goToMap">Visiter la map</button></a>	
			if(est_admin){
				$("#menu_user").append('<a href="testeur"><button class="button_user">Zone de test</button></a>');
			}
			$("#menu_user").append('<a href="deconnexion"><button class="button_user">Déconnexion</button></a>');
		}
		else{
			$("#menu_user").append('<a href="connexion"><button class="button_user">Connexion</button></a>');
			$("#menu_user").append('<a href="inscription"><button class="button_user">Inscription</button></a>');
		}

		gray='rgb(169, 169, 169)'
		darkgray= 'rgb(128, 128, 128)'
		//l'affichage du menu de profile
		$("#profil").click(()=>{
			
			$("#menu_user").toggleClass("show");
			if ($("#menu_user").hasClass("show")){
				$("#icon_user").css('color',darkgray);
				// $('#icon_user').off('hover');
				$('#icon_user').off('mouseenter mouseleave');
			}
			else{
				$("#icon_user").css('color',gray);
				$("#icon_user").hover( ()=> $("#icon_user").css('color',darkgray), ()=>$("#icon_user").css('color',gray) );
			}
			
		});

		$("#icon_user").hover( ()=> $("#icon_user").css('color',darkgray), ()=>$("#icon_user").css('color',gray) );
		

	}
	

	function createVerionSelector(search_v){
		//par défaut la dernière version  
		search_version = search_v[search_v.length -1];

		//création de selecteur search_version	 (pour les admins)
		if(est_admin){

			var select= '</b><span>Version du scraper:  </span>';
			select+= '<select name="search_version" id="search_version">';
			select+= '<option value="'+search_v[search_v.length -1]+'">Dernière Version</option>';
			$.each(search_v,(index,version)=>{
				select+= '<option value="'+version+'">'+version+'</option>';
			});
			select+= '</select><br>';
			$("#search_version").replaceWith(select);

		}
	} 
	     
	
	//création du checkbox du choix de nouvellle recherche
	(()=>{
		let html='<input type="checkbox" name="scraping_input" id="scraping_input" value="scraping">';
		html+= '<label for="scraping_input" id="scraping_label">Effectuer une nouvelle recherche sur Reddit </label>'+space(2)
		html+= '<span class="material-icons icon_info" title="Effectuer une nouvelle recherche vous permet de\ntrouver des photos plus récentes sur Reddit.\nToutefois, la recheche va durer quelques instants">info</span>'
		$("#scraping_div").replaceWith(html);
	})();


	//en cliquant sur le bouton
	$("#submit").click(function(){
		
		if(!is_scraping){
			is_scraping=true;
			var valeur= $("#select_input").val();   //récupérer la valeur de l'input pays dans le format France,FR
			var scraping=  $("input[id='scraping_input']").is(':checked');
			$("#scraping_input").prop("checked", false);
			if( valeur == "" ){
				$("#error").show();
			}
			else{
				$("#error").hide();
				var pays= valeur.split(",");      //séparer le nom de pays et le code de pays 
				var search_version="1.00"
				if(est_admin)
					search_version = $("#search_version").val();	
					
				//envoyer la requête ajax pour demander l'éxecution de la focntion scraping dans le script python
				$.ajax({
					type:"GET",
					url:"/scraping",
					datatype:"json",
					data:{                     //passer les paramètres au script python
						country:pays[0],
						country_code:pays[1],
						search_version: search_version,
						scraping: scraping,
						nombre_image: parseInt($("#nombre_image").val())
					},
					beforeSend:startAnimation ,
					success: createMap        //appeler la fonction pour créer la carte si la requête a réussi
				}).fail(printError);          //envoyer un message d'error si la requête a échoué
			}
		
		}
		
	});


	function printError(error){    //afficher la page d'erreur 
		
		console.error("status: "+error['status']+"\nstatusText: "+error['statusText']);
		$('body').replaceWith(error['responseText']);
		
	}

	//la fonction pour créer la carte, data est l'objet json renvoyer par la fonction scraping de python
	function createMap(data){      
		//se placer sur la carte
		is_scraping=false;
		stopAnimation();
		mymap.setView([ data['head']['country']['lat'],  data['head']['country']['lng']], 6);

		var oms = new OverlappingMarkerSpiderfier(mymap);


		/*oms.addListener('click', function(marker) {
				popup.setContent(marker.desc);
				popup.setLatLng(marker.getLatLng());
				map.openPopup(popup);
		});*/

		//placer les images
		$.each(data['results'],function(i,image){
			if(!hasExtension(image['img_url'])){
				image['img_url']+= '.jpg';
			}
			var myIcon = L.icon({
				iconUrl:image['img_url'],
				iconSize: [60,40]
			});
			var marker =new L.marker( [ image['lat'] , image['lng'] ],{icon: myIcon});
			mymap.addLayer(marker);
			oms.addMarker(marker);
			
		});

		function hasExtension(str){
			return (str.includes('jpg') || str.includes('png') || str.includes('svg')) || str.includes('gif');
		}



		// événement déclanché uniquement en single click (on vérifie le double click)
		var clickCount = 0;

		$(".leaflet-marker-pane > img")
		.on("click", function() {
			clickCount++;
			if (clickCount === 1) {
				singleClickTimer = setTimeout(() => {
					clickCount = 0;
					var src = $(this).attr('src');                                     // chercher l'url de l'image 
					var index = data['results'].findIndex(x => x.img_url == src);          // chercher l'index de l'image dans la liste des images
					var image = data['results'][index];                                // rÃ©cupÃ©rer l'image comme un dictionnaire 
					afficheImage(image);
				}, 300);
			} else if (clickCount === 2) {
				clearTimeout(singleClickTimer);
				clickCount = 0;
			}
		});

	}

	function afficheImage(image){

		
		/*
			image['name'] nous donne la location choisi par geoname
			image['text'] nous donne le text sur l'image
			image['lng'] nous donne la longitude
			image['alt'] nous donne la laltitude 
			image['img_url'] nous donne l'url de l'image 
			image['link'] nous donne l'url de la post (la publication sur reddit)
			image['date'] nous donne la date de l'image tel que:
				image['date']['year']   nous donne l'annÃ©e 
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
		var html='<div id="replace">';
		html+= '<div id="imageDiv" style="background-image: url(\''+image['img_url']+'\')"><img id="image" src="'+image['img_url']+'"></div>';
		html+='<p id="first_line">';
		html+= '<img id="imageProfil" src="'+image['author']['icon']+'">';
		html+='<a title="Voir le profil" style="text-decoration : none" href="'+image['author']['profile']+'" target="_blank">';
		html+= '<span id="nameProfil">'+image['author']['name']+'</span></a>';
		html+= '<a href="'+image['img_url']+'" title="Voir en plein d\'écran " target="_blank"><i class="material-icons icoc_clickable">aspect_ratio</i></a>';
		html+= '<a href="'+image['link']+'" title="Voir dans le site original" target="_blank"><i class="material-icons launch icoc_clickable">launch</i></a>';
		html+= '</p>';
		html+='<p id="second_line">';
		html+= '<i class="material-icons icon">location_on</i>';
		html+= '<span class="time_location">'+image['name']+'</span>';
		html+= '<i class="material-icons icon">access_time</i>';
		html+= '<span class="time_location">Le '+image['date']['day']+' '+monthFormat(image['date']['month'])+' '+image['date']['year']+'   à   '+timeFormat(image['date']['hour'])+':'+timeFormat(image['date']['min'])+'</span>';
		html+= '</p>';
		
		//partie texte
		originalText= '<p id="text" style="font-size:'+fontSize(image['text'])+'px">'+image['text']+'</p>';
		html+= originalText;
		
		//partie signalement
		originalReport= '<p id="report"><span class="material-icons icon_feedback" title="Votre réponse nous aidera à améliorer la recherche">feedback</span>'+space(1);
		originalReport+= '<span> Aidez-nous 🙏🏼 | </span>';
		originalReport+='<span id="text_report"><span style="font-weight: bold"> '+image['name']+'</span>, est-il le lieu indiqué dans le commantaire ci-dessus ?</span><br>';
		originalReport+= space(8)+'<button class="signaler" id="Oui">Oui'+space(2)+'<span class="material-icons icon_thumb" style="color:#2f55a4">thumb_up</span></button>'+space(3);
		originalReport+= '<button class="signaler" id="Non">Non'+space(2)+'<span class="material-icons icon_thumb" style="color:#a52a2a">thumb_down</span></button>';
		originalReport+= '</p>';
		html+= originalReport; 
		html+= '</div>';
		$("#replace").replaceWith(html);
		
		// vérifier que cette image n'a pas déjà été signalé
		if ($.inArray(image['img_url'],reported_images) != -1){
			reportDone({'status':'OK'});
		}
		else{
			addEventReport(image);
		}

	}


	function addEventReport(image){
		$(".signaler").click(function(){ 

			//compléter les inforamtions du signalement
			var list_words=[];
			var value;

			if ($(this).attr('id') == 'Oui'){
				value="OK";
				sendReport(image,value,list_words);
				//ajouter l'url à la liste des images signalées
				reported_images.push(image['img_url']);
			}
			
			else{
				value = 'NOT_OK';
				createCheckbox(image);

				$('#annuler').click(function(){
					$("#text").replaceWith(originalText);
					$('#report').replaceWith(originalReport);
					addEventReport(image);
				});

				$('#envoyer').click(function(){
					list_words= getWords();
					$("#text").replaceWith(originalText);
					sendReport(image,value,list_words);
					//ajouter l'url à la liste des images signalées
					reported_images.push(image['img_url']);
				});
				
			}
			
		});
	}

	function getWords(){
		var values=[];      //liste de tous les mots choisis
		
		$.each( $("input[class='checkbox']:checked") , function(){
			values.push($(this).val());         //remplir la liste avec les mots  
		});

		return values;
	}

	function sendReport(image,value,list_words){
		$.ajax({
			type:"POST",
			url:"/report",
			contentType: "application/json;charset=UTF-8",
			data: JSON.stringify({'image':image,'value':value,'list_words':list_words}),
			success: reportDone        //appeler la fonction pour créer la carte si la requête a réussi
		}).fail(printError);          //envoyer un message d'error si la requête a échoué
	}
 
	function reportDone(data){
		$(".signaler").remove();
		if(data['status']=='OK')
			$("#text_report").replaceWith('<span>Votre réponse a été envoyé. Nous vous remercions pour votre aide.</span>');
		else
			$("#text_report").replaceWith('<span>Un problème s\'est produite !</span>');
	}

	function timeFormat(time){
		if(time<10)
			time="0"+time;
		return time;
	}
	function monthFormat(month){
		var str;
		switch (month){
			case 1: str="janvier";break;
			case 2: str="février";break;
			case 3: str="mars";break;
			case 4: str="avril";break;
			case 5: str="mai";break;
			case 6: str="juin";break;
			case 7: str="juillet";break;
			case 8: str="août";break;
			case 9: str="septembre";break; 
			case 10: str="octobre ";break;
			case 11: str="novembre";break;
			case 12: str="décembre";break;
			default: str="Format indéfini";
		}
		return str;

	}

	function fontSize(str){
		l = str.length;
		if(l<350)
			return '18';
		else if(l<490)
			return '16';
		else 
			return '13';
	}
	function space(n){
		str='';
		while(n>0){
			str+='&nbsp';
			n--;
		}
		return str;
	}



	function createCheckbox(image,list_words){
		var text= image['text'];
		var html='<p id="text" style="font-size:'+fontSize(text)+'px">';
		var pos;
		$.each(image['tag_list'],function(i,mot){
			if(mot[1]!="," && mot[1]!="PUN" && mot[1]!="SENT"){
				pos= text.indexOf(mot[0]);   //récupérer l'index de début du mot
				html+= text.substring(0,pos);      //mettre ce qu'il y a avant dans la balise p
				html+= '<label for="checkbox'+i+'" class="label">'+mot[0]+'</label>';      //créer le label
				html+= '<input type="checkbox" name="checkbox'+i+'" id="checkbox'+i+'" class="checkbox" value="'+mot[0]+'">';  //créer le checkbox
				text= text.substr(pos+mot[0].length);     //supprimer le mot et ce qu'il y a avant de la phrase originale
			}
		});
		html+= text + '</p>';     //mettre le reste de la phrase dans la balise p
		$("#text").replaceWith(html);

		$('.checkbox').change( function(){       
			if( $(this).is(':checked') ){
				var color = "yellow";
			}
			else{
				var color = "#e6ffff";
			}
			$("label[for='"+$(this).attr('id')+"']").css("background-color",color);
		});

		html= '<p id="report"><span class="material-icons icon_feedback" title="Votre réponse nous aidera à améliorer la recherche">feedback</span>'+space(1);
		html+='<span id="text_report">Veuillez choisir dans le commantaire le(s) mot(s) indiquant le lieu correct </span><br>';
		html+= space(8)+'<button class="signaler" id="annuler"> annuler </button>'+space(3);
		html+= '<button class="signaler" id="envoyer">envoyer '+space(1)+'<span class="material-icons send_icon" >send</span></button>';
		html+= '</p>';
		$('#report').replaceWith(html);

	}

	function startAnimation(){
		var animation= "<div id=\"animation\"><div id=\"content\"><div id=\"circle1\"></div><div id=\"circle2\"></div></div></div>";
		$("#parametres_profil").append(animation);
	}
	function stopAnimation(){
		$("#animation").remove();
	}
});


