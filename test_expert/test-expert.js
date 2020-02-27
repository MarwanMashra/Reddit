$(document).ready(function(){

	$.ajax({		//récupération des donné via requete ajax
		type:"GET",
		url: "", //json
		datatype:"json",
		data:{
			userid: "//userid"
		},
		success: test //apel de la fonction test
	}).fail(printError);

	function printError(error){
		alert("ERROR !!!");
		console.error(error);
	}

	function test(data){

		let i = 0;
		while((data['results'][i]['img']) (data['results'][i]['curenttest']))
	
			var myImg = new Image();				//affiche l'image
			myImg.src=(data['results'][i]['img']); 

						//print test


	}


	$("#Oui").click(function(){
		if ((data['results'][i]['curenttest'])==1){ //si on est au premier test
			if((data['results'][i]['nbmauvais'])+1 == 2){
				// supr img de mongoGB
			}

			else{
				if ((data['results'][i]['nbrp']) + 1  == 3){ //si le nombre de réponce = 3
						// curent test + 1
						//nbmauvais =0
						//nbrp = 0 
						
				}else{
						// nbrp = nbrp +1
						// nbmauvais = nbmauvais +1
				}
			}
		}else{
			if((data['results'][i]['nbrp']) + 1  == 3){
				// géoname sujet du testg  
						// mise a jour mongogb (mauvais/curenttest/usserlist/nbrp/nbmauvais a Null)
			}
			else{
					//nbrp+1
			}
		}


		i++;
	});
	$("#Non").click(function(){
		if ((data['results'][i]['curenttest'])==1){ //si on est au premier test
			if ((data['results'][i]['nbrp']) + 1  == 3){ //si le nombre de réponce = 3
						// curent test + 1 
						
			}else{
						// nbrp = nbrp +1
			}
		}else{
					if ((data['results'][i]['nbmauvais']) + 1  == 2){ //si le nombre de réponce = 3
						// curent test + 1 
						// nbmauvais = 0
						// nbrp = 0
						
				}else{
						// nbrp = nbrp +1
						// nbmauvais = nbmauvais +1
				}

		}





		i++;
	});
});