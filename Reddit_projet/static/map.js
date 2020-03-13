$(document).ready(function(){

	//création de la carte
	var mymap = L.map('mapid');                 
	L.tileLayer('http://{s}.google.com/vt/lyrs=s,h&x={x}&y={y}&z={z}',{
    		maxZoom: 20,
    		subdomains:['mt0','mt1','mt2','mt3']
			}).addTo(mymap);

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
					country_code:pays[1]
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

	function printError(error){
		$("#animation").remove();
		alert("ERROR !!!");
		console.error(error);
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
	}

	// affichage des images quand on les clique 
	$(".leaflet-marker-icon").click(function(){                      // quand on clique sur une image sur la carte
		var src = $(this).attr('src');                                     // chercher l'url de l'image 
		alert("src "+src);
		var index = data['results'].findIndex(x => x.img == src);          // chercher l'index de l'image dans la liste des images
		alert("index "+index);
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
