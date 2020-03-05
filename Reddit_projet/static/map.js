$(document).ready(function(){

	//création de la carte
	var mymap = L.map('mapid');                 
	L.tileLayer('http://{s}.google.com/vt/lyrs=s,h&x={x}&y={y}&z={z}',{
    		maxZoom: 20,
    		subdomains:['mt0','mt1','mt2','mt3']
			}).addTo(mymap);

	//en cliquant sur le bouton
	$("#submit").click(function(){
		alert("commencer la recherch");
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
				success: createMap        //appeler la fonction pour créer la carte si la requête a réussi
			}).fail(printError);          //envoyer un message d'error si la requête a échoué
		}
		
	});
	
	function printError(error){
		alert("ERROR !!!");
		console.error(error);
	}

	//la fonction pour créer la carte, data est l'objet json renvoyer par la fonction scraping de python
	function createMap(data){      
		//se placer sur la carte
		mymap.setView([ data['head']['country']['lat'],  data['head']['country']['lng']], 5);                                
		//placer les images
		$.each(data['results'],function(i){
			var myIcon = L.icon({
				iconUrl:data['results'][i]['img'],
				iconSize: [60,'auto']
			});
			L.marker( [ data['results'][i]['lat'] , data['results'][i]['lng'] ],{icon: myIcon}).addTo(mymap);
		});
	}


});
