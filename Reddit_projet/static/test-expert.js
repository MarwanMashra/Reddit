$(document).ready(function(){

	document.getElementById("Oui1").disabled = true; //
	document.getElementById("Non1").disabled = true; // empecher l'utilisateur de clicker avant que tout soit prêt
	document.getElementById("Oui2").disabled = true; //
	document.getElementById("Non2").disabled = true; //


	$.ajax({		//récupération des donné via requete ajax
		url: "/expert_init", //json
	}).async=false;


	$.ajax({		//récupération des donné via requete ajax
		type:"GET",
		url: "/get_results", //json
		datatype:"json",
		data:{
			value: "NOT_OK",
			tester: "NDebart"
		},
		success: test //apel de la fonction test
	}).fail(printError).async=false;

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
			/*$.ajax({		//récupération des donné via requete ajax
				url: "/expert_init", //json
				data:{
					results : array
				}
			}).async=false;*/



			document.write("<div>Plus de données veuillez actualisé </div>")
			document.write(JSON.stringify(array))

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