$(document).ready(function(){

	document.getElementById("Oui1").disabled = true; //
	document.getElementById("Non1").disabled = true; // empecher l'utilisateur de clicker avant que tout soit prêt
	document.getElementById("Oui2").disabled = true; //
	document.getElementById("Non2").disabled = true; //


	$.ajax({		//Initialisation de la collection 'Testeurs' de la base de données si elle n'existe pas
		url: "/expert_init",
		//Garantie que la récupération des résultats se lance après expert_init
		success: function(){
			$.ajax({
				type:"GET",
				url: "/get_results",
				datatype:"json",
				data:{
					value: "NOT_OK",
					tester: "NDebart"
				},
				success: test //Appel de la fonction test
			}).fail(printError).async=false;
		}
	}).async=false;

	function printError(error){
		alert("ERROR !!!");
		console.error(error);
	}
	i = 0;
	k =0;
	array=[]
	dict ={
		'img_url': "",
		search_version: "",
		nom_location : []
	}


	function test(data){
		myData = data
		j = 0;



		if (myData['results'][i] != null){
			


			document.getElementById("title").innerHTML=myData['results'][i]['title'];

			//sparce titre
			res =myData['results'][i]['title'].split(" ");
			var question1 = "".concat('Est ce que ',res[k],' est un élément de la localisation ?');
			document.getElementById("question 1").innerHTML= question1;
			document.getElementById("question 2").innerHTML= "question2";

			document.getElementById("Oui2").disabled = false;	//
			document.getElementById("Non2").disabled = false;	// activé les boutons
			document.getElementById("Oui1").disabled = false;	//
			document.getElementById("Non1").disabled = false;	//
			
		}else{

			document.write("<div>Plus de données; veuillez actualiser.</div>");

			$.ajax({
				type:"POST",
				url: "/send_results",
				contentType: "application/json;charset=UTF-8",
				data: JSON.stringify({
					results: array,
					tester: JSON.stringify(myData['tester'])
				}),
			}).fail(printError).async=false;

		}

	
	}




		$("#Oui1").click(function(){

			document.getElementById("Oui1").disabled = true;
			document.getElementById("Non1").disabled = true;
			dict['nom_location'].push('true')

			j++;
			if (j==2){
				k++
				if (res[k]==null){

					dict['search_version']=myData['results'][i]['search_version']
					dict['img_url']=myData['results'][i]['img_url']
					
						array.push(dict)
					
					dict ={
						img_url: "",
						search_version: "",
						nom_location : ""
					}

					k=0
					i++
				}
				test(myData)
			}
		});
		$("#Non1").click(function(){
			document.getElementById("Oui1").disabled = true;
			document.getElementById("Non1").disabled = true; 
			dict['nom_location'].push('false')


			j++;
			if (j==2){
				k++
				if (res[k]==null){

					dict['search_version']=myData['results'][i]['search_version']
					dict['img_url']=myData['results'][i]['img_url']
					
					array.push(dict)
					
					dict ={
						img_url: "",
						search_version: "",
						nom_location : []
					}

					k=0
					i++
				}
				test(myData)
			}
		});
		$("#Oui2").click(function(){
			document.getElementById("Oui2").disabled = true;
			document.getElementById("Non2").disabled = true; 


			j++;
			if (j==2){
				k++
				if (res[k]==null){

					dict[search_version]=myData['results'][i]['search_version']
					dict['img_url']=myData['results'][i]['img_url']
					
					array.push(dict)

					dict ={
						img_url: "",
						search_version: "",
						nom_location : []
					}

					k=0
					i++
				}
				test(myData)
			}
		});
		$("#Non2").click(function(){
			document.getElementById("Oui2").disabled = true;
			document.getElementById("Non2").disabled = true; 

			j++;
			if (j==2){
				k++
				if (res[k]==null){

					dict['search_version']=myData['results'][i]['search_version']
					dict['img_url']=myData['results'][i]['img_url']

					array.push(dict)

					dict ={
						img_url: "",
						search_version: "",
						nom_location : []
					}

					k=0
					i++
				}
				test(myData)
			}

		});



});