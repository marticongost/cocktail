/* Inicialització en català per a l'extenció 'calendar' per jQuery. */
/* Writers: (joan.leon@gmail.com). */

	jQuery.datepicker.regional['ca'] = {
		clearText: 'Netejar', clearStatus: '',
		closeText: 'Tancar', closeStatus: '',
		prevText: '&#x3c;Ant', prevStatus: '',
		prevBigText: '&#x3c;&#x3c;', prevBigStatus: '',
		nextText: 'Seg&#x3e;', nextStatus: '',
		nextBigText: '&#x3e;&#x3e;', nextBigStatus: '',
		currentText: 'Avui', currentStatus: '',
		monthNames: ['Gener','Febrer','Mar&ccedil;','Abril','Maig','Juny',
		'Juliol','Agost','Setembre','Octubre','Novembre','Desembre'],
		monthNamesShort: ['Gen','Feb','Mar','Abr','Mai','Jun',
		'Jul','Ago','Set','Oct','Nov','Des'],
		monthStatus: '', yearStatus: '',
		weekHeader: 'Sm', weekStatus: '',
		dayNames: ['Diumenge','Dilluns','Dimarts','Dimecres','Dijous','Divendres','Dissabte'],
		dayNamesShort: ['Dug','Dln','Dmt','Dmc','Djs','Dvn','Dsb'],
		dayNamesMin: ['Dg','Dl','Dt','Dc','Dj','Dv','Ds'],
		dayStatus: 'DD', dateStatus: 'D, M d',
		firstDay: 1, 
		initStatus: '', isRTL: false,
		onSelect: function () {
		    var class_name = 'timepickr' + jQuery(this).attr('id');
		    if(jQuery('.' + class_name)){
		        jQuery('.' + class_name).focus();
		    }
        },
        onClose: function () {
            var class_name = 'timepickr' + jQuery(this).attr('id');
		    if(jQuery(this).val()==""){
		        jQuery('.' + class_name).val('');
		    }
        }
    };
	jQuery.datepicker.setDefaults(jQuery.datepicker.regional['ca']);



	jQuery.datepicker.regional['es'] = {
		clearText: 'Limpiar', clearStatus: '',
		closeText: 'Cerrar', closeStatus: '',
		prevText: '&#x3c;Ant', prevStatus: '',
		prevBigText: '&#x3c;&#x3c;', prevBigStatus: '',
		nextText: 'Sig&#x3e;', nextStatus: '',
		nextBigText: '&#x3e;&#x3e;', nextBigStatus: '',
		currentText: 'Hoy', currentStatus: '',
		monthNames: ['Enero','Febrero','Marzo','Abril','Mayo','Junio',
		'Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'],
		monthNamesShort: ['Ene','Feb','Mar','Abr','May','Jun',
		'Jul','Ago','Sep','Oct','Nov','Dic'],
		monthStatus: '', yearStatus: '',
		weekHeader: 'Sm', weekStatus: '',
		dayNames: ['Domingo','Lunes','Martes','Mi&eacute;rcoles','Jueves','Viernes','S&aacute;dabo'],
		dayNamesShort: ['Dom','Lun','Mar','Mi&eacute;','Juv','Vie','S&aacute;b'],
		dayNamesMin: ['Do','Lu','Ma','Mi','Ju','Vi','S&aacute;'],
		dayStatus: 'DD', dateStatus: 'D, M d',
		firstDay: 1, 
		initStatus: '', isRTL: false,
		onSelect: function () {
		    var class_name = 'timepickr' + jQuery(this).attr('id');
		    if(jQuery('.' + class_name)){
		        jQuery('.' + class_name).focus();
		    }
        },
        onClose: function () {
            var class_name = 'timepickr' + jQuery(this).attr('id');
		    if(jQuery(this).val()==""){
		        jQuery('.' + class_name).val('');
		    }
        }
    };
	jQuery.datepicker.setDefaults(jQuery.datepicker.regional['es']);	



	jQuery.datepicker.regional['en'] = {
		firstDay: 0, 
		initStatus: '', isRTL: false,
	    onSelect: function () {
		    var class_name = 'timepickr' + jQuery(this).attr('id');
		    if(jQuery('.' + class_name)){
		        jQuery('.' + class_name).focus();
		    }
        },
        onClose: function () {
            var class_name = 'timepickr' + jQuery(this).attr('id');
		    if(jQuery(this).val()==""){
		        jQuery('.' + class_name).val('');
		    }
        }
    };
    jQuery.datepicker.setDefaults(jQuery.datepicker.regional['en']);		



    jQuery.datepicker.setDefaults(jQuery.datepicker.regional['']);