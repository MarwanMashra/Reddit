$(document).ready(function(){
	//on utilise des variables globales pour ne pas devoir les passer aux fonctions à chaque fois

	var SEARCH_VERSION= "1.00";
	var NB_TEST;              //stocke le nombre des test à effectuer 
	var data;                 //stocke les tests 
	var index=0;              //pour parcouir la liste des tests 
	var result={};            //stocker le résultat
		

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
			div+= '<p>Bonjour '+pseudo+', vous avez '+nbtest+' tests à faire, veuillez choisir le nombre de tests que vous souhaitez effectuer.</p>';
			div+= '<select name="nbtest" id="nbtest">';
			div+= '<option value="'+nbtest+'">Pas de limite</option>';
			for (var i = 1; i <= nbtest; i++) {
				div+= '<option value="'+i+'">'+i+'</option>';
			}
			div+= '</select>';
			div+= '<select name="search_version" id="search_version">';
			div+= '<option value="'+search_version[search_version.length -1]+'">Dernière Version</option>';
			$.each(search_version,(index,version)=>{
				div+= '<option value="'+version+'">'+version+'</option>';
			});
			div+= '</select>';
			div+= '<button id="start">Commencer le test</button>';
			div+= '</div>';
			$("#ici").replaceWith(div);
		}

		$('#goToMap').show();

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
		//préparer la variable result 
		result['search_version']= SEARCH_VERSION;
		result['img_url']=[];
		result['results']=[];
		$.each(data['results'], function(i,element){
			result['img_url'].push(element['img_url']);
			result['results'].push({'lieux_choisis':[]});
		});
		
		//cacher le bouton visiter la map
		$('#goToMap').hide();

		//lancer le test en créant le premier formulaire
		createForm();     
	}


	function titreUtili(){
		var title=data['results'][index]['tag_list'];
		var name=data['results'][index]['name'].split(" ");	
		var html="<p>Lieu choisi par le script:<br>";

		$.each(title,function(index,mots){
				if(name.includes(mots[0]))
					html+= '<span style="background-color: #FFFF00">'+mots[0]+'</span> ';
				else
					html+= mots[0]+' ';
		});
		html+= "</p>";

		return html;
	}

	function createForm(){
	
		//créer le formulaire
		var form='';             
		form+= '<form id="testForm" class="test">';
		form+= '<p class="question_tag"> Question ('+(index+1)+'/'+NB_TEST+') : </p>';

		//insértion des éléments dans le formulaire 
		form+= titreUtili();
		form+= genCheckbox();
		form+= genkeywords();
		
		//checkbox "je sais pas"
		form+= '<br><p>-------------------------------------------------------</p>';
		form+= '<input type="checkbox" name="je_sais_pas" id="je_sais_pas" value="je_sais_pas">';
		form+= '<label for="je_sais_pas">Je sais pas, je passe cette question.</label><br>';
	
		form+= '<br><button type="submit" name="continue" form="testForm" value="continue">Valider</button>'
		if (index+1 < NB_TEST){     //pour ne pas montrer ce choix avec la dernière question
   			form+= '<button type="submit" name="stop" form="testForm" value="stop">Valider et quitter</button>'
		}
		form+= '</form>';

		//insérer la formulaire
		$(".test").replaceWith(form);      

		//changer la couleur des mots choisis
		$(".checkbox").change( function(){       
			if( $(this).is(':checked') ){
				var color = "yellow";
			}
			else{
				var color = "white";
			}
			$("label[for='"+$(this).attr('id')+"']").css("background-color",color);
		});

		$("#testForm > button").click(function(){

			if(!($("input[id='je_sais_pas']").is(':checked'))){                 //vérifier qu'il a pas cocher la casee "je sais pas" (à faire)
 				updateResult();       //mettre à jour la liste des résultats 
			}
			console.log(result);
	       

	        index+=1;

			if( $(this).attr('value')=="continue" ){
				if(index < NB_TEST){       //continuer les tests
					
					createForm();

				}
				else{        //test terminé
					send();
					createPageEnd();
					$('#goToMap').show();
				}
				
			}
			else{       //test arrêté
				send();
				createPageEnd();
				$('#goToMap').show();
			}
		});

	}

	function genCheckbox(){
		var tag_list= data['results'][index]['tag_list'];
		var checkbox="<br>Veuillez choisir les mots indiquant le lieu:<br>";
		$.each(tag_list,function(i,tag_mot){
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
		
		});
		return checkbox;
	}

	function genkeywords(){
		var loc_list=data['results'][index]['location_list'];
		var proper_loc=[];
		$(loc_list).each(function(i,loc){
			if(typeof loc !== "number"){
				proper_loc.push(loc);
			}
		});
		var keywords="<br><br><p>Est-ce que le lieu est présent dans ces mots clés :";
		//keywords+='<p>'+data['results'][index]['location_list']+'</p>';
		keywords+='<p>'+proper_loc+'</p>';
		keywords+='<input type="checkbox" id="keywords" name="keywords" value="keywords" >';
		keywords+='<label for="keywords"> Oui, il est présent</label></p>';

		return keywords;

	}
 

	function updateResult(){
		var values=[];      //liste de tous les mots choisis

		$.each( $("input[value!='keywords']:checked") , function(){
			values.push($(this).val());         //remplir la liste avec les mots mots 
		});

		$.each(data['results'][index]['tag_list'], function(i,mot){            //parcourir la liste tag_list
            result['results'][index]['lieux_choisis'].push( $.inArray(mot[0],values) != -1 );   //tester si le mot est présent dans values et mettre le booléen dans la liste des résultats
		});
		
        result['results'][index]['suffisant']= $("input[id='keywords']").is(':checked');

	}

	function send(){
			$.ajax({
				type:"POST",
				url: "/send_results",
				contentType: "application/json;charset=UTF-8",
				data: JSON.stringify(result)
			}).fail(printError);

	}

	function createPageEnd(){
		var html='<p>Fin de test. Toute notre équipe vous remercie ^_^ </p>';
		$(".test").replaceWith(html);
	}


});
