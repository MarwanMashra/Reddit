$(document).ready(function(){
	
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
					scraping: $("input[id='scraping_input']").is(':checked')
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
	function createMap(data){      
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

		// affichage des images quand on les clique 
		$(".leaflet-marker-pane > img").click(function(){                      // quand on clique sur une image sur la carte
			var src = $(this).attr('src');                                     // chercher l'url de l'image 
			var index = data['results'].findIndex(x => x.img == src);          // chercher l'index de l'image dans la liste des images
			var image = data['results'][index];                                // rÃ©cupÃ©rer l'image comme un dictionnaire 

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
			html+= '<p>'+image['text']+'</p>';
			html+= '<img src="'+image['img']+'">';
			html+= '<button id="signaler"> signaler </button>';
			html+= '</div>';
			$("#replace").replaceWith(html);

			$("#signaler").click(function(){
				$.ajax({
					type:"POST",
					url:"/report",
					contentType: "application/json;charset=UTF-8",
					data: JSON.stringify(image),
					success: reportDone        //appeler la fonction pour créer la carte si la requête a réussi
				}).fail(printError);          //envoyer un message d'error si la requête a échoué
			});

		});

	}

	function reportDone(){
		$("#signaler").replaceWith("<p>L'image a été sigalée. Notre équipe de testeurs va vérifier le placement de l'image.");
	}
	
	
});
