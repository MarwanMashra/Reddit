$(document).ready(function(){
	//on utilise des variables globales pour ne pas devoir les passer aux fonctions à chaque fois

	var SEARCH_VERSION= "1.00";
	var NB_TEST;              //stocke le nombre des test à effectuer 
	var data;                 //stocke les tests 
	var index=0;              //pour parcouir la liste des tests 
	var result={};            //stocker le résultat
	var valuesCheckbox=[];
	var image;
	var DEBUG= false; 
		
	//requête pour demander le nombre de test qu'on a à effectuer
	$.ajax({
		type:"GET",
		url:"/get_count",
		success: createDiv    //créer le premier élément de la page qui demande au testeur le nombre de test à effectuer
	}).fail(printError);

	function printError(error){    //afficher la page d'erreur 
		console.error("status: "+error['status']+"\nstatusText: "+error['statusText']);
		$('body').replaceWith(error['responseText']);
	}

	function createDiv(count){

		var nbtest=count['nbtest'];
		var pseudo=count['pseudo'];
		var search_version=count['versions'];
		if (count!=0) {
			var div= '<div id="divStart" class="test">';
			div+= '<p>Bonjour <span style="font-weight: bold">'+pseudo+'</span>, vous avez '+nbtest+' tests à réaliser.</p>'
			div+= '<p>Veuillez choisir le nombre de tests que vous souhaitez effectuer : ';
			div+= '<select name="nbtest" id="nbtest">';
			div+= '<option value="'+nbtest+'">Pas de limite</option>';
			for (var i = 1; i <= nbtest; i++) {
				div+= '<option value="'+i+'">'+i+'</option>';
			}
			div+= '</select></p>';
			div+= '<p>Veuillez choisir la version du code que vous voulez tester : ';
			div+= '<select name="search_version" id="search_version">';
			div+= '<option value="'+search_version[search_version.length -1]+'">Dernière Version</option>';
			$.each(search_version,(index,version)=>{
				div+= '<option value="'+version+'">'+version+'</option>';
			});
			div+= '</select></p><br>';
			div+= '<button id="start">Commencer le test</button>';
			div+= '</div><br>';
			$("#container").append(div);
		}

		addEventStart();
		

	}

	function addEventStart(){
		//requête pour demander les données à traiter
		$("#start").click(function(){
			NB_TEST = parseInt($("#nbtest").val());
			SEARCH_VERSION = $("#search_version").val();
			$.ajax({
				type:"GET",
				url:"/get_results",
				datatype:"json",
				data:{                    
					value:"NOT_OK",
					version: SEARCH_VERSION,
					limit: NB_TEST
				},
				success: startTest   //lancer la préparation avant le test
			}).fail(printError); 
		});
	}

	function startTest(d){
		//enregister les données dans une variable glabale data
		data=d; 
		NB_TEST= data['results'].length
		console.log(data['results']);
		//préparer la variable result 
		result['search_version']= SEARCH_VERSION;
		result['img_url']=[];
		result['results']=[];
		$.each(data['results'], function(i,element){
			result['img_url'].push(element['img_url']);
			result['results'].push({'lieux_choisis':[]});
		});
		
		//lancer le test en créant le premier formulaire
		createForm();     
	}


	function choiceScript(){
		var html='<p class="question_phrase">Lieu choisi par les algorithmes:</p><p>'+image['name']+'</p>';

		return html;
	}

	function choiceUser(){
		var html='<p class="question_phrase">Lieu proposé par l\'utilisateur:</p><p>'+concateListe(image['test_list'],false,true)+'</p>';

		return html;
	}

	function createForm(){
		
		image=data['results'][index];
		console.log(image);
		
		//créer le formulaire
		var form='';             
		form+= '<div id="testForm" class="test">';
		form+= '<p class="question_tag"> Image ('+(index+1)+'/'+NB_TEST+') : </p>';
		form+= '<div id="imageDiv" style="background-image: url(\''+image['img_url']+'\')"><img id="image" src="'+image['img_url']+'"></div>';
		form+= '<p id="text">'+image['text']+'</p><br>'
		form+= '<div id="contenuTest">'
		//insértion des éléments dans le formulaire 
		form+= choiceScript();
		form+= choiceUser();
		form+= genCheckbox();

		/*form+= genkeywords();
		//checkbox "je sais pas"
		form+= '<br><p>-------------------------------------------------------</p>';
		form+= '<input type="checkbox" name="je_sais_pas" id="je_sais_pas" value="je_sais_pas">';
		form+= '<label for="je_sais_pas">Je sais pas, je passe cette question.</label><br>';
	
		form+= '<br><button value="continue">Valider</button>'
		if (index+1 < NB_TEST){     //pour ne pas montrer ce choix avec la dernière question
   			form+= '<button value="stop">Valider et quitter</button>'
		}*/

		form+= '<br><br><button value="passe">Passer cette question</button>';
		form+= '<button value="cherche">Chercher des résultats</button>';
		form+= '</div>';

		form+= '</div>';

		//insérer la formulaire
		$(".test").replaceWith(form);      
		addEventButton();     //ajouter les événements des boutons

		//changer la couleur des mots choisis
		$(".checkbox").change( function(){       
			if( $(this).is(':checked') ){
				var color = "yellow";
			}
			else{
				var color = "transparent";
			}
			$("label[for='"+$(this).attr('id')+"']").css("background-color",color);
		});

	}


	function addEventButton(){
		$("#contenuTest > button").click(function(){

			var button=$(this).attr('value');
			
			if( button=="cherche"){
				getValuesCheckbox();    //récuperer les valeurs des checkboxs dans la liste valuesCheckbox
				createSeceondForm();    //cerhcehr des résultats géonames et créer la deuxième partie de formulaire
			}
			else{    //donc c'est soit "passe" soit "continue" soit "stop"

				if(button != "passe"){
					updateResult();
				}

				index+=1;

				if(index < NB_TEST && (button == "passe" || button == "continue")){
					createForm();
				}
				else{
					send();
					createPageEnd();
					$('#goToMap').show();
				}

			}

	        
		});
	}

	function createSeceondForm(){
		createSeceondFormSuite(["Lieu_1","Lieu_2","Lieu_3","Lieu_4"]);
		/*$.ajax({
			type:"GET",
			url:"/get_results_geonames",
			datatype: "json",
			data:{    
				location: concateListe(valuesCheckbox,true,false),
				country: image['country_code']
			},
			beforeSend:startAnimation,
			success: createSeceondFormSuite,
		}).fail(printError);	
		*/
		
	}
	function createSeceondFormSuite(list_locations){
		stopAnimation();
	
		var html= '<div id="contenuTest">';
		html+= '<p class="question_phrase">Vous avez choisi le lieu suivant :</p>'
		html+= concateListe(valuesCheckbox,true,true);
		html+= '<br><p class="question_phrase">Voici les résultats trouvés, veuillez choisir la plus proche (ou Aucun) :</p>';
		html+= genRadio(list_locations);
		html+= '<br>'+genkeywords();
		
		if (index+1 < NB_TEST){     //pour ne pas montrer ce choix avec la dernière question
			html+= '<br><br><button value="stop">Valider et quitter</button>';
		}
		html+= '<button value="continue">Valider</button>';
		html+= '</div>';
		
		$("#contenuTest").replaceWith(html);
		addEventButton();

	}

	function genCheckbox(){
		var tag_list= image['tag_list'];
		var text= image['text'];
		var html='<p class="question_phrase">Veuillez choisir les mots indiquant le lieu:</p><p>';
		var pos;
		$.each(tag_list,function(i,mot){
			if(mot[1]!="," && mot[1]!="PUN" && mot[1]!="SENT"){
				pos= text.indexOf(mot[0]);   //récupérer l'index de début du mot
				html+= text.substring(0,pos);      //mettre ce qu'il y a avant dans la balise p
				html+= '<label for="checkbox'+i+'" class="label">'+mot[0]+'</label>';      //créer le label
				html+= '<input type="checkbox" name="checkbox'+i+'" id="checkbox'+i+'" class="checkbox" value="'+mot[0]+'">';  //créer le checkbox
				text= text.substr(pos+mot[0].length);     //supprimer le mot et ce qu'il y a avant de la phrase originale
			}
		});
		html+= '.</p>';

		return html;
	}
	/*
		

		if(tag_mot[1]=="PUN" || tag_mot[1]=="SENT"){      //si le mot est une poncutation 
			checkbox+= tag_mot[0];
			}
			else if(tag_mot[1]=="CTY"){
				checkbox+= ' '+tag_mot[0];
			}
			else{               //créer un checkbox pour le mot
				checkbox+= '<label for="checkbox'+i+'" class="label">  '+tag_mot[0]+'</label>'
				checkbox+= '<input type="checkbox" name="checkbox'+i+'" id="checkbox'+i+'" class="checkbox" value="'+tag_mot[0]+'">'
			}
			html+= text + '</p>';     //mettre le reste de la phrase dans la balise p
		*/

	function genkeywords(){
		var loc_list=image['location_list'];
		var proper_loc=loc_list.filter(x => isNaN(x));

		var keywords='<p class="question_phrase">Est-ce que le lieu est présent dans ces mots clés :';
		//keywords+='<p>'+image['location_list']+'</p>';
		keywords+='<p>'+proper_loc+'</p>';
		keywords+='<input type="radio" id="Oui" name="keywords" value="Oui" >';
		keywords+='<label for="Oui"> Oui, il est présent</label></p>';
		keywords+='<input type="radio" id="Non" name="keywords" value="Non" checked>';
		keywords+='<label for="Non"> Non, il n\'est pas présent</label></p>';

		return keywords;

	}
 
	function getValuesCheckbox(){
		valuesCheckbox=[];      //liste de tous les mots choisis
		var i;
		$.each( $("input[class='checkbox']:checked") , function(){
			id = $(this).prop("id");
			i = parseInt(id.substring(8));
			valuesCheckbox.push([i,$(this).val()]);         //remplir la liste avec les mots mots 
		});
	}

	function updateResult(){
		$.each(image['tag_list'], function(i,mot){            //parcourir la liste tag_list
            result['results'][index]['lieux_choisis'].push( $.inArray(mot[0],valuesCheckbox) != -1 );   //tester si le mot est présent dans values et mettre le booléen dans la liste des résultats
		});
		
		result['results'][index]['suffisant']= ($("input[name='keywords']:checked").val() == "Oui");
		result['results'][index]['geonames_chosen_result']= ($("input[name='location']:checked").val());

	}

	function send(){
		if (!DEBUG){
			$.ajax({
				type:"POST",
				url: "/send_results",
				contentType: "application/json;charset=UTF-8",
				data: JSON.stringify(result)
			}).fail(printError);
		}
		else{
			console.log(result);
		}
		
	}

	function concateListe(liste,hasIndex,affichage){
		var str="";
		if(hasIndex){
			$.each(liste,function(i,mot){
				if((i<liste.length-1 && liste[i][0]==liste[i+1][0]-1) || (i==liste.length-1)){
					str+=mot[1]+" ";	
				}
				else{
					if(affichage){
						str+=mot[1]+", ";
					}
					else{
						str+=mot[1]+",";
					}
				}
				
			});
		}
		else{
			$.each(liste,function(i,mot){
				str+=mot+" ";	
			});
		}
		return str.substring(0, str.length - 1);
	}

	function genRadio(list_locations){
		var html="";
		$.each(list_locations,function(i,location){
			html+=  '<input type="radio" id="location'+i+'" name="location" value="'+location+'">';
			html+=  '<label for="location'+i+'"> '+location+'</label><br>';
		});

		html+= '<input type="radio" id="Aucun" name="location" value="None" checked>';
		html+= '<label for="Aucun">Aucun</label>';

		return html;
	}

	function genRadio(list_locations){
		var html="";
		$.each(list_locations,function(i,location){
			html+=  '<input type="radio" id="location'+i+'" name="location" value="'+location+'">';
			html+=  '<label for="location'+i+'"> '+location+'</label><br>';
		});

		html+= '<input type="radio" id="Aucun" name="location" value="None" checked>';
		html+= '<label for="Aucun">Aucun</label>';

		return html;
	}

	function createPageEnd(){
		var html='<p>Fin de test. Toute notre équipe vous remercie 🙏🏼 </p><br>';
		html+= '<a href="testeur"><button value="restart">Relancer le test</button></a>';
		$(".test").replaceWith(html);
		
	}

	function startAnimation(){
		var animation= "<div id=\"animation\"><div id=\"content\"><div id=\"circle1\"></div><div id=\"circle2\"></div></div></div>";
		$("body").append(animation);
	}

	function stopAnimation(){
		$("#animation").remove();
	}
	
	$("#goToMap").click(sendExit);
	$("#deconnexion").click(sendExit);
	function sendExit(){
		if(index>0){
			send();
		}
	}



});
