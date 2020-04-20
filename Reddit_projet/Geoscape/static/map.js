$(document).ready(function(){

	//si vous êtes en train de tester, mettez le à true, vous serez pas obligez à lancer une recherche à chaque fois
	var DEBUG=false;

	//création de la carte
	var mymap = L.map('mapid');                 
	L.tileLayer('http://{s}.google.com/vt/lyrs=s,h&x={x}&y={y}&z={z}',{
    		maxZoom: 20,
    		subdomains:['mt0','mt1','mt2','mt3']
			}).addTo(mymap);

	//création de selecteur search_version	
	function createVerionSelector(search_version){
		var select= '<select name="search_version" id="search_version">';
		select+= '<option value="'+search_version[search_version.length -1]+'">Dernière Version</option>';
		$.each(search_version,(index,version)=>{
			select+= '<option value="'+version+'">'+version+'</option>';
		});
		select+= '</select><br>';
		$("#search_version").replaceWith(select);
	}

	//requête get_list_version
	$.ajax({
		type:"GET",
		url:"/get_list_version",
		success: createVerionSelector,
		error:  ()=>{var search_version=["1.00"];createVerionSelector(search_version);}
	});          
	

	//en cliquant sur le bouton
	$("#submit").click(function(){
		var valeur= $("#select_input").val();   //récupérer la valeur de l'input pays dans le format France,FR
		if( valeur == "" ){
			$("#error").show();
		}
		else{
			$("#error").hide();
			var pays= valeur.split(",");      //séparer le nom de pays et le code de pays 
			//envoyer la requête ajax pour demander l'éxecution de la focntion scraping dans le script python
			$.ajax({
				type:"GET",
				url:"/scraping",
				datatype:"json",
				data:{                     //passer les paramètres au script python
					country:pays[0],
					country_code:pays[1],
					search_version: $("#search_version").val(),
					scraping: $("input[id='scraping_input']").is(':checked'),
					nombre_image: parseInt($("#nombre_image").val())
				},
				beforeSend:startAnimation ,
				success: createMap        //appeler la fonction pour créer la carte si la requête a réussi
			}).fail(printError);          //envoyer un message d'error si la requête a échoué
		}
		
	});
	
	function startAnimation(){
		var animation= "<div id=\"animation\"><div id=\"content\"><div id=\"circle1\"></div><div id=\"circle2\"></div></div></div>";
		$("body").append(animation);
	}


	function printError(error){    //afficher la page d'erreur 
		
		console.error("status: "+error['status']+"\nstatusText: "+error['statusText']);
		$('body').replaceWith(error['responseText']);
		
	}

	//la fonction pour créer la carte, data est l'objet json renvoyer par la fonction scraping de python
	/*function createMap(data){      
		//se placer sur la carte
		$("#animation").remove();
		mymap.setView([ data['head']['country']['lat'],  data['head']['country']['lng']], 5);                                
		//placer les images
		$.each(data['results'],function(i){
			var myIcon = L.icon({
				iconUrl:data['results'][i]['img'],
				iconSize: [60,40]
			});
			L.marker( [ data['results'][i]['lat'] , data['results'][i]['lng'] ],{icon: myIcon}).addTo(mymap);
		});
		*/
	function createMap(data){      
		//se placer sur la carte
		$("#animation").remove();
		mymap.setView([ data['head']['country']['lat'],  data['head']['country']['lng']], 6);

		var oms = new OverlappingMarkerSpiderfier(mymap);


		/*oms.addListener('click', function(marker) {
				popup.setContent(marker.desc);
				popup.setLatLng(marker.getLatLng());
				map.openPopup(popup);
		});*/

		//placer les images
		$.each(data['results'],function(i){
			var myIcon = L.icon({
				iconUrl:data['results'][i]['img_url'],
				iconSize: [60,40]
			});
			var marker =new L.marker( [ data['results'][i]['lat'] , data['results'][i]['lng'] ],{icon: myIcon});
			mymap.addLayer(marker);
			oms.addMarker(marker);
		});


		// événement déclanché uniquement en single click (on vérifie le double click)
		var timer = 0;
		var delay = 300;
		var prevent = false;
/*
		$(".leaflet-marker-pane > img")
		.on("click", function() {
			timer = setTimeout(() => {
			if (!prevent) {
				var src = $(this).attr('src');                                     // chercher l'url de l'image 
				var index = data['results'].findIndex(x => x.img == src);          // chercher l'index de l'image dans la liste des images
				var image = data['results'][index];                                // rÃ©cupÃ©rer l'image comme un dictionnaire 
				afficheImage(image);
			}
			prevent = false;
			}, delay);
		})
		.on("dblclick", function() {
			clearTimeout(timer);
			prevent = true;
		});
*/
				
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
			image['img'] nous donne l'url de l'image 
			image['url'] nous donne l'url de la post (la publication sur reddit)
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
		html+='<p>';
		html+= '<img id="imageProfil" src="'+image['author']['icon']+'">';
		html+='<a style="text-decoration : none" href="'+image['author']['profile']+'" target="_blank">';
		html+= '<span id="nameProfil">'+image['author']['name']+'</span></a>';
		html+= '<i class="material-icons icon">location_on</i>';
		html+= '<span class="time_location">'+image['name']+'</span>';
		html+= '<i class="material-icons icon">access_time</i>';
		html+= '<span class="time_location">Le '+image['date']['day']+' '+monthFormat(image['date']['month'])+' '+image['date']['year']+'   à   '+timeFormat(image['date']['hour'])+':'+timeFormat(image['date']['min'])+'</span>';
		html+= '<i class="material-icons fullscreen">fullscreen</i>';
		html+= '</p>';
		html+= '<p id="text">'+image['text']+'</p>';
		html+= '<button id="signaler"> Cette photo est mal placée ? </button>';
		html+= '</div>';
		$("#replace").replaceWith(html);

		$("#signaler").click(function(){//
			$.ajax({
				type:"POST",
				url:"/report",
				contentType: "application/json;charset=UTF-8",
				data: JSON.stringify(image),
				success: reportDone        //appeler la fonction pour créer la carte si la requête a réussi
			}).fail(printError);          //envoyer un message d'error si la requête a échoué
		});
	}
 
	function reportDone(data){
		if(data['status']=='OK')
			$("#signaler").replaceWith("<p>L'image a été sigalée. Notre équipe de testeurs va vérifier le placement de l'image.</p>");
		else
			$("#signaler").replaceWith("<p>Un problème s'est produit</p>");
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
	
});
