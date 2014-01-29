function countdown(element, zieldatum) {
	startDatum=new Date(); // Aktuelles Datum
	startDatum.setHours(startDatum.getUTCHours())
	// Countdown berechnen und anzeigen, bis Ziel-Datum erreicht ist
	if(startDatum<zielDatum)  {
	
		var tage=0, stunden=0, minuten=0, sekunden=0;
		
		// Tage
		while(startDatum.getTime()+(24*60*60*1000)<zielDatum) {
			tage++;
			startDatum.setTime(startDatum.getTime()+(24*60*60*1000));
		}
		
		// Stunden
		stunden=Math.floor((zielDatum-startDatum)/(60*60*1000));
		startDatum.setTime(startDatum.getTime()+stunden*60*60*1000);
		
		// Minuten
		minuten=Math.floor((zielDatum-startDatum)/(60*1000));
		startDatum.setTime(startDatum.getTime()+minuten*60*1000);
		
		// Sekunden
		sekunden=Math.floor((zielDatum-startDatum)/1000);
		
		var tage_ = tage;
		// Anzeige formatieren
		(tage!=1)?tage=tage+" Tage,  ":tage=tage+" Tag,  ";
		(stunden!=1)?stunden=stunden+" Stunden,  ":stunden=stunden+" Stunde,  ";
		(minuten!=1)?minuten=minuten+" Minuten  und  ":minuten=minuten+" Minute  und  ";
		if(sekunden<10) sekunden="0"+sekunden;
		(sekunden!=1)?sekunden=sekunden+" Sekunden":sekunden=sekunden+" Sekunden";
		
		if (tage_ > 14){
			element.innerHTML = "findet statt am " + zieldatum.getDate()+"."+(zieldatum.getMonth()+1)+"."+zieldatum.getFullYear()+"!";
		}else{
			element.innerHTML= "noch " + tage + stunden + minuten + sekunden + " verbleibend!";
		}
		element.className = "label label-primary";
		
		if (tage_ < 3){
			element.className = "label label-danger";
		}else if (tage_ < 7){
			element.className = "label label-warning";
		}
		setTimeout(function() { countdown(element);},1000);
	}
	// Bei abgelaufenen Spieltagen: nichts anzeigen
		else {
			element.innerHTML = "abgelaufen am " + zieldatum.getDate()+"."+(zieldatum.getMonth()+1)+"."+zieldatum.getFullYear()+"!";
			element.className = "label label-default";
		}
}
  
function mark_verein(verein_id){
	var trs = document.getElementsByName("tabelle_verein_" + verein_id);
	for (var i = 0; i < trs.length; ++i){
		trs[i].className="active";
	}
}
function clear_marked_verein(){
	var tabelle = document.getElementsByName("tabelle_verein");
	for (var i = 0; i < tabelle.length; ++i){
		var trs = tabelle[i].getElementsByTagName("tr");
		for (var j = 0; j < trs.length; ++j){
			trs[j].className = ""
		}
	}
}
