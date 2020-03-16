$(document).ready(function(){
	//on utilise des variables globales pour ne pas devoir les passer aux fonctions à chaque fois
	var NB_TEST;              //stocke le nombre des test à effectuer 
	var data;                 //stocke les tests 
	var index=0;              //pour parcouir la liste des tests 
	var result={};            //stocker le résultat

	//requête pour demander le nombre de test qu'on a à effectuer
	$.ajax({
			type:"GET",
			url:"/get_cohunt",
			success: createDiv    //créer le premier élément de la page qui demande au testeur le nombre de test à effectuer
		}).fail(printError); 


	function printError(error){    //afficher la page d'erreur 
		console.error("status: "+error['status']+"\nstatusText: "+error['statusText']);
		$('body').replaceWith(error['responseText']);
	}

	function createDiv(count){

		var nbtest=count['nbtest'];
		var pseudo=count['pseudo'];
		if (count!=0) {
			var div= '<div id="divStart" class="test">';
			div+= '<p>Bonjour '+pseudo+', Vous avez '+nbtest+' test à faire, veuillez choisir le nombre de test que vous voulez passer</p>';
			div+= '<select name="nbtest" id="nbtest">';
			div+= '<option value="'+nbtest+'">Pas de limit</option>';
			for (var i = 1; i <= nbtest; i++) {
				div+= '<option value="'+i+'">'+i+'</option>';
			}
			div+= '</select>';
			div+= '<button id="start">Commencer le test</button>';
			div+= '</div>';
			$("#ici").replaceWith(div);
		}

		//requête pour demander les données à traiter
		$("#start").click(function(){
			NB_TEST = parseInt($("#nbtest").val());
			$.ajax({
				type:"GET",
				url:"/get_results",
				datatype:"json",
				data:{                    
					value:"NOT_OK",
					version:"1.00",
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
		result['search_version']=data['results'][0]['search_version'];
		result['img_url']=[];
		result['results']=[];
		$.each(data['results'], function(i,element){
			result['img_url'].push(element['img_url']);
			result['results'].push([]);
		});
		//lancer le test en créant la première formulaire 
		createForm();     
	}   


	function createForm(){
		//créer la formulaire
		var form='';             
		form+= '<form id="testForm" class="test">';
		form+= '<p class="question_tag"> Question ('+(index+1)+'/'+NB_TEST+') : </p>';

		//insértion des éléments dans le formulaire 
		form+= genCheckbox();
		

		form+= '<br><button type="submit" name="continue" form="testForm" value="continue">Valider</button>'
		if (index+1 < NB_TEST){     //pour ne pas montrer ce choix avec la dernière question
   			form+= '<button type="submit" name="stop" form="testForm" value="stop">Valider et quitter</button>'
		}
		form+= '</form>';

		//insérer la formulaire
		$(".test").replaceWith(form);      

		//changer la couleur des mots choisis
		$("input[type='checkbox']").change( function(){       
			if( $(this).is(':checked') ){
				var color = "yellow";
			}
			else{
				var color = "white";
			}
			$("label[for='"+$(this).attr('id')+"']").css("background-color",color);
		});


		$("#testForm > button").click(function(){

			if(true){                 //vérifier qu'il a pas cocher la casee "je sais pas" (à faire)
 				updateResult();       //mettre à jour la liste des résultats 
	            console.log(result);
	        }

	        index+=1;

			if( $(this).attr('value')=="continue" ){
				if(index < NB_TEST){       //continuer les tests
					
					createForm();

				}
				else{        //test terminé
					
					//send result
				}
				
			}
			else{       //test arrêté

				//send result
			}
		});

	}

	function genCheckbox(){
		var tag_list= data['results'][index]['tag_list'];
		var checkbox="";
		$.each(tag_list,function(i,tag_mot){
			if(tag_mot[1]=="PUN" || tag_mot[1]=="SENT"){      //si le mot est une poncutation 
				checkbox+= tag_mot[0];
			}
			else{               //créer un checkbox pour le mot
				checkbox+= '<label for="checkbox'+i+'" class="label">  '+tag_mot[0]+'</label>'
				checkbox+= '<input type="checkbox" name="checkbox'+i+'" id="checkbox'+i+'" class="checkbox" value="'+tag_mot[0]+'">'
			}
		
		});
		return checkbox;
	}

	function updateResult(){
		var values=[];      //liste de tous les mots choisis

		$.each( $("input[type='checkbox']:checked") , function(){
			values.push($(this).val());         //remplir la liste avec les mots mots 
		});

		$.each(data['results'][index]['tag_list'], function(i,mot){            //parcourir la liste tag_list
            result['results'][index].push( $.inArray(mot[0],values) != -1 );   //tester si le mot est présent dans values et mettre le booléen dans la liste des résultats
        });

	}


});