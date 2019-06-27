/*global $, jQuery, localStorage, window, angular, alert, document, console, confirm, require, $source, $output */
/*jshint unused:false */
/*jshint plusplus: false, devel: true, nomen: true, indent: 4, maxerr: 50 */
/* https://codepen.io/netsi1964/pres/bdMxvr */ 
// This function is just a codepen related util for the lazy programmer :-)
"use strict";
(function defineVarsFromClassName() {
		var needVar = $("[class]"),
				definedVars = "",
				i,
				ii,
				classes,
				sVarName,
				sClassName,
				$this,
				$us;
		for (i = 0; i < needVar.length; i++) {
				$this = $(needVar[i]);
				classes = $this.attr("class").split(" ");
				for (ii = 0; ii < classes.length; ii++) {
						sClassName = $.trim(classes[ii]);
						if (sClassName.length > 0) {
								$us = $("." + sClassName);
								sVarName = "$" + sClassName.replace(/\-/g, "_");
								if (typeof window[sVarName] === "undefined") {
										window[sVarName] = $us;
										definedVars += " " + sVarName;
								}
						}
				}
		}
		return definedVars;
})();

// INCLUDE FROM HERE - csvToHtml

/**
 * Converts a CSV string to object with rows and header
 * @param   {String} sCSV    A CSV string
 * @param   {Object} options {
 *                         seperator: string "The CSV col selerator" [";"]
 *                         hasHeader: bool [true]
 *                         headerPrefix: string ["COL]  }
 * @returns {Object} {
 * headers: array of headers,
 * rows: array of rows (including header)
 *  }
 */
function convertToArray(sCSV, options) {
		var result = {
						headers: null,
						rows: null
				},
				firstRowAt = 0,
				tds,
				first,
				cols;
		options = options || {};
		options = $.extend(options, {
				seperator: ",",
				hasHeader: true,
				headerPrefix: "COL"
		});

		// Create header
		tds = sCSV.split("\x0a");
		first = tds[0].split(options.seperator);
		if (options.hasHeader) {
				result.headers = first;
				result.headers = result.headers.map(function(header) {
						return header.replace(/\//g, "_");
				});
				firstRowAt = 1;
		} else {
				result.headers = first.map(function(header, i) {
						return options.headerPrefix + i;
				});
		}

		// Create rows
		cols = result.headers.length;
		result.rows = tds.map(function(row, i) {
				return row.split(options.seperator);
		});
		return result;
}

function tag(element, value, className) {
		if(!className){
			return "<" + element + ">" + value + "</" + element + ">";
		}
		return "<" + element + ' class="' + className +'"' + ">" + value + "</" + element + ">";
}

function toHTML(arr) {
		var sTable = "<table class=\"table table-striped sticky_table\"><thead>";
		arr.map(function(row, i) {
				var sRow = "";
				row.map(function(cell, ii) {
						var tagname = (i === 0) ? "th" : "td";
						sRow += tag(tagname, cell, arr[0][ii] ? arr[0][ii] : '');
				});

				sTable += tag("tr", sRow, false) + ((i === 0) ? "</thead><tbody>" : "");
		});
		return sTable + "</tbody></table>";
}

function csvToHtml($source, $output, options) {
				var sCSV = $source.val(),
						result = convertToArray(sCSV, options || {});
				$output.html(toHTML(result.rows));
				$('#output > table > tbody tr td').each(function(a,b){
						$(this).each(function(c,d){
							var className = $(this).attr('class');
							var text = $(this).text();
							if(className == 'price'){
								var price_close = parseFloat($(this).parent().find('.price_close').text())
								if(!price_close){
									var price_target = $(this).parent().find('.price_target').text()
									$(this).parent().find('.price_close').text(price_target)
									$(this).parent().find('.price_close').addClass('success')
								}
							}else if(className == 'units'){
								var units = parseFloat($(this).parent().find('.units').text())
								if(units > 0){
									$(this).parent().find('.units').addClass('info')
								}else{
									$(this).parent().find('.units').addClass('warning')
								}
							}else if(className == 'pl'){
								var pl = parseFloat($(this).parent().find('.pl').text())
								if(pl > 0){
									$(this).parent().find('.pl').addClass('success')
								}else{
									$(this).parent().find('.pl').addClass('danger')
								}
							}
							if(text == 'True'){
								$(this).addClass('danger')
							}
							// var text = '#output > table > tbody > tr:nth-child(' + b + ') > td.' + className;
							// var $target = $(text)
							// console.log($target)

						}
					)
				});
		}
		// INCLUDE TO HERE - csvToHtml

$(function() {
	csvToHtml($('#source'), $('#output'));
});
