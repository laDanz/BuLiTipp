function countdown(element, zieldatum) {
	startDatum=new Date(); // Aktuelles Datum
	
	// Countdown berechnen und anzeigen, bis Ziel-Datum erreicht ist
	if(startDatum<zielDatum)  {
	
		var jahre=0, monate=0, tage=0, stunden=0, minuten=0, sekunden=0;
		
		// Jahre
		while(startDatum<zielDatum) {
			jahre++;
			startDatum.setFullYear(startDatum.getFullYear()+1);
		}
		startDatum.setFullYear(startDatum.getFullYear()-1);
		jahre--;
		
		// Monate
		while(startDatum<zielDatum) {
			monate++;
			startDatum.setMonth(startDatum.getMonth()+1);
		}
		startDatum.setMonth(startDatum.getMonth()-1);
		monate--;
		
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
		
		// Anzeige formatieren
		if(jahre>0){
			(jahre!=1)?jahre=jahre+" Jahre,  ":jahre=jahre+" Jahr,  ";
		}else{
			jahre=""
		}          
		if(monate>0){
			(monate!=1)?monate=monate+" Monate,  ":monate=monate+" Monat,  ";
		}else{
			monate=""
		}
		(tage!=1)?tage=tage+" Tage,  ":tage=tage+" Tag,  ";
		(stunden!=1)?stunden=stunden+" Stunden,  ":stunden=stunden+" Stunde,  ";
		(minuten!=1)?minuten=minuten+" Minuten  und  ":minuten=minuten+" Minute  und  ";
		if(sekunden<10) sekunden="0"+sekunden;
		(sekunden!=1)?sekunden=sekunden+" Sekunden":sekunden=sekunden+" Sekunden";
		
		element.innerHTML=
			"noch " + jahre + monate + tage + stunden + minuten + sekunden + " verbleibend!";
		element.className = "label label-primary";
		setTimeout(function() { countdown(element);},1000);
	}
	// Bei abgelaufenen Spieltagen: nichts anzeigen
		else {
			element.innerHTML = "abgelaufen am " + zieldatum.getDay()+"."+zieldatum.getMonth()+"."+zieldatum.getFullYear()+"!";
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
