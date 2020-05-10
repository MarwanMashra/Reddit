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

		if(DEBUG) console.log(data['results']);
		NB_TEST= data['results'].length
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
				}

			}

	        
		});
	}

	function createSeceondForm(){
		if(valuesCheckbox.length > 0){
			$.ajax({
				type:"GET",
				url:"/get_results_geonames",
				datatype: "json",
				data:{    
					location: concateListe(valuesCheckbox,true,false),
					country_code: image['country_code']
				},
				beforeSend:startAnimation,
				success: createSeceondFormSuite,
			}).fail(printError);	
		}

		else{
			createSeceondFormSuite([]);
		}
		
		
	}
	function createSeceondFormSuite(locations_list){
		if(DEBUG) console.log(locations_list)
		stopAnimation();

		//enlever la répétition 
		locations_list= unique(locations_list)

		var html= '<div id="contenuTest">';
		html+= '<p class="question_phrase">Vous avez choisi le lieu suivant :</p>'
		if(valuesCheckbox.length >0){
			html+= concateListe(valuesCheckbox,true,true);
		}
		else{
			html+= "-----";
		}
		
		html+= '<br><p class="question_phrase">Voici les résultats trouvés, veuillez choisir la plus proche (ou Aucun) :</p>';
		html+= genRadio(locations_list);
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
		var html='<p class="question_phrase">Veuillez choisir les mots indiquant le lieu (s\'il y en a):</p><p>';
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

	function genkeywords(){
		/*
		var loc_list=image['location_list'];
		var proper_loc=loc_list.filter(x => isNaN(x));
		*/

		var keywords='<br><p class="question_phrase">La location, est-elle présente dans le titre ?</p>';
		//keywords+='<p>'+image['location_list']+'</p>';
		keywords+='<p>'+image['scraped_title']+'</p>';
		keywords+='<p><input type="radio" id="Oui" name="keywords" value="Oui" >';
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
		var list_checkbox=[];
		$.each(valuesCheckbox,function(i,element){
			list_checkbox.push(element[1]);
		});

		$.each(image['tag_list'], function(i,mot){            //parcourir la liste tag_list
            result['results'][index]['lieux_choisis'].push( $.inArray(mot[0],list_checkbox) != -1 );   //tester si le mot est présent dans values et mettre le booléen dans la liste des résultats
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

	function genRadio(locations_list){
		var html='<p class="radio" style="text-align:left;margin-left:30%">';
		var maxLength= getMaxLength(locations_list);
		maxLength+=10;
		var nbSpace;

		$.each(locations_list,function(i,location){
			nbSpace= maxLength - location[0].length;
			html+=  '<input type="radio" id="location'+i+'" name="location" value="'+location[0]+'">';
			html+=  '<label for="location'+i+'"> '+location[0]+'</label>'+space(nbSpace)+' ('+feature_class(location[1])+')<br>';
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

	function unique(listlist) {
		var list=[]
		var result = [];

		$.each(listlist, function(i, element) {
			if ($.inArray(element[0], list) == -1){
			result.push(element)
			list.push(element[0]);
			}
		});

		return result;
	}

	function feature_class(c){
		var str;
		switch (c) {
			case 'A':
				str= "Divisions administratives";
				break;
			case 'H':
				str= "Eaux superficielles";
				break;
			case 'L':
				str= "Parcs / Réserves / Régions";
				break;
			case 'P':
				str= "Lieux peuplés";
				break;
			case 'R':
				str= "Routes";
				break;
			case 'S':
				str= "Structures";
				break;
			case 'T':
				str= "Montagnes / Îles";
				break;
			case 'U':
				str= "Sous-marine";
				break;
			case 'V':
				str= "Forêts";
				break;
		
			default:
				str="inconnu";
				break;
		}

		return str;
	}

	function space(n){
		str='';
		while(n>0){
			str+='&nbsp';
			n--;
		}
		return str;
	}
	function getMaxLength(list){
		var max=0;
		$.each(list,function(i,element){
			if(element[0].length > max){
				max= element[0].length ;
			}
		});

		return max;
	}

});
/*GeoNames feature classes ('fcl' dans le JSON de Geonames, champ 'feature_class' de geocoder)
		A   Administrative divisions
		H   Surface waters
		L   Parks/reserves/regions
		P   Populated places
		R   Roads
		S   Structures
		T   Mountains/islands
		U   Undersea
		V   Woodlands
*/
