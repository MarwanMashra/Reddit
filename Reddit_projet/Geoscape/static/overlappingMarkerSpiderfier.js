(function(){/*
 OverlappingMarkerSpiderfier
https://github.com/jawj/OverlappingMarkerSpiderfier-Leaflet
Copyright (c) 2011 - 2012 George MacKerron
Released under the MIT licence: http://opensource.org/licenses/mit-license
Note: The Leaflet maps API must be included *before* this code
*/
(function(){
	var q={}.hasOwnProperty,r=[].slice;
	null!=this.L&&(
		this.OverlappingMarkerSpiderfier=function(){
			function n(c,b){
				var a,e,g,f,d=this;
				this.map=c;
				null==b&&(b={});
				for(a in b)
					q.call(b,a)&&(
						e=b[a],
						this[a]=e
						);
				this.initMarkerArrays();
				this.listeners={};
				f=["zoomend"];
				e=0;
				for(g=f.length;e<g;e++)
					a=f[e],this.map.addEventListener(a,function(){
						return d.unspiderfy()
					})
			}
			var d,k;
			d=n.prototype;
			d.VERSION="0.2.6";
			k=2*Math.PI;
			d.keepSpiderfied=!1;
			d.nearbyDistance=30;
			d.circleSpiralSwitchover=9;
			d.circleFootSeparation=25;
			d.circleStartAngle=k/12;
			d.spiralFootSeparation=50;
			d.spiralLengthStart=11;
			d.spiralLengthFactor=5;
			d.legWeight=1.5;
			d.legColors={usual:"#222",highlighted:"#f00"};
			d.initMarkerArrays=function(){
				this.markers=[];
				return this.markerListeners=[]
			};
			d.addMarker=function(c){
				var b,a=this;
				if(null!=c._oms)
					return this;
				c._oms=!0;
				b=function(){
					return a.spiderListener(c)};
					c.addEventListener("dblclick",b);
					this.markerListeners.push(b);
					this.markers.push(c);
					return this};
					d.getMarkers=function(){
						return this.markers.slice(0)
					};
					d.removeMarker=function(c){
						var b,a;
						null!=c._omsData&&this.unspiderfy();
						b=this.arrIndexOf(this.markers,c);
						if(0>b)
							return this;
						a=this.markerListeners.splice(b,1)[0];
						c.removeEventListener("dblclick",a);
						delete c._oms;
						this.markers.splice(b,1);
						return this
					};
					d.clearMarkers=function(){
						var c,b,a,e,g;
						this.unspiderfy();
						g=this.markers;
						c=a=0;
						for(e=g.length;a<e;c=++a)
							b=g[c],c=this.markerListeners[c],b.removeEventListener("dblclick",c),delete b._oms;
						this.initMarkerArrays();
						return this};
						d.addListener=function(c,b){
							var a,e;
							(null!=(e=(a=this.listeners)[c])?e:a[c]=[]).push(b);
							return this
						};
						d.removeListener=function(c,b){
							var a;
							a=this.arrIndexOf(this.listeners[c],b);
							0>a||this.listeners[c].splice(a,1);
							return this
						};
						d.clearListeners=function(c){
							this.listeners[c]=[];
							return this
						};
						d.trigger=function(){
							var c,b,a,e,g,f;
							b=arguments[0];
							c=2<=arguments.length?r.call(arguments,1):[];
							b=null!=(a=this.listeners[b])?a:[];f=[];
							e=0;
							for(g=b.length;e<g;e++)
								a=b[e],f.push(a.apply(null,c));
							return f
						};
						d.generatePtsCircle=function(c,b){
							var a,e,g,f,d;
							g=this.circleFootSeparation*(2+c)/k;e=k/c;d=[];
							for(a=f=0;0<=c?f<c:f>c;a=0<=c?++f:--f)
								a=this.circleStartAngle+a*e,d.push(new L.Point(b.x+g*Math.cos(a),b.y+g*Math.sin(a)));
							return d
						};
						d.generatePtsSpiral=function(c,b){
							var a,e,g,f,d;
							g=this.spiralLengthStart;
							a=0;d=[];
							for(e=f=0;0<=c?f<c:f>c;e=0<=c?++f:--f)
								a+=this.spiralFootSeparation/g+5E-4*e,e=new L.Point(b.x+g*Math.cos(a),b.y+g*Math.sin(a)),g+=k*this.spiralLengthFactor/a,d.push(e);
							return d
						};
						d.spiderListener=function(c){
							var b,a,e,g,f,d,h,k,l;
							(b=null!=c._omsData)&&this.keepSpiderfied||this.unspiderfy();
							if(b)
								return this.trigger("dblclick",c);
							g=[];f=[];
							d=this.nearbyDistance*this.nearbyDistance;
							e=this.map.latLngToLayerPoint(c.getLatLng());
							l=this.markers;
							h=0;
							for(k=l.length;h<k;h++)
								b=l[h],this.map.hasLayer(b)&&(a=this.map.latLngToLayerPoint(b.getLatLng()),this.ptDistanceSq(a,e)<d?g.push({marker:b,markerPt:a}):f.push(b));
							return 1===g.length?this.trigger("dblclick",c):this.spiderfy(g,f)};
							d.makeHighlightListeners=function(c){
								var b=this;
								return{highlight:function(){
									return c._omsData.leg.setStyle({color:b.legColors.highlighted})
								},unhighlight:function(){
									return c._omsData.leg.setStyle({color:b.legColors.usual})
								}
							}
						};
						d.spiderfy=function(c,b){
							var a,e,g,d,p,h,k,l,n,m;
							this.spiderfying=!0;m=c.length;a=this.ptAverage(function(){var a,b,e;
								e=[];
								a=0;
								for(b=c.length;a<b;a++)k=c[a],e.push(k.markerPt);
									return e}());
							d=m>=this.circleSpiralSwitchover?this.generatePtsSpiral(m,a).reverse():this.generatePtsCircle(m,a);
							a=function(){
								var a,b,k,m=this;
								k=[];a=0;
								for(b=d.length;a<b;a++)
									g=d[a],e=this.map.layerPointToLatLng(g),n=this.minExtract(c,function(a){
										return m.ptDistanceSq(a.markerPt,g)
									}),h=n.marker,p=new L.Polyline([h.getLatLng(),e],{color:this.legColors.usual,weight:this.legWeight,clickable:!1}),this.map.addLayer(p),h._omsData={usualPosition:h.getLatLng(),leg:p},this.legColors.highlighted!==this.legColors.usual&&(l=this.makeHighlightListeners(h),h._omsData.highlightListeners=l,h.addEventListener("mouseover",l.highlight),h.addEventListener("mouseout",l.unhighlight)),h.setLatLng(e),h.setZIndexOffset(1E6),k.push(h);
								return k
							}.call(this);
							delete this.spiderfying;this.spiderfied=!0;
							return this.trigger("spiderfy",a,b)};
							d.unspiderfy=function(c){
								var b,a,e,d,f,k,h;
								null==c&&(c=null);
								if(null==this.spiderfied)
									return this;
								this.unspiderfying=!0;
								d=[];
								e=[];
								h=this.markers;
								f=0;
								for(k=h.length;f<k;f++)
									b=h[f],null!=b._omsData?(
										this.map.removeLayer(b._omsData.leg),
										b!==c&&b.setLatLng(b._omsData.usualPosition),b.setZIndexOffset(0),a=b._omsData.highlightListeners,null!=a&&(b.removeEventListener("mouseover",a.highlight),b.removeEventListener("mouseout",a.unhighlight)),delete b._omsData,d.push(b)):e.push(b);
								delete this.unspiderfying;
								delete this.spiderfied;this.trigger("unspiderfy",d,e);
								return this
							};
							d.ptDistanceSq=function(c,b){
								var a,e;
								a=c.x-b.x;
								e=c.y-b.y;
								return a*a+e*e
							};
							d.ptAverage=function(c){
								var b,a,e,d,f;
								d=a=e=0;
								for(f=c.length;d<f;d++)
									b=c[d],a+=b.x,e+=b.y;
								c=c.length;
								return new L.Point(a/c,e/c)};
								d.minExtract=function(c,b){
									var a,d,g,f,k,h;
									g=k=0;
									for(h=c.length;k<h;g=++k)
										if(f=c[g],f=b(f),"undefined"===typeof a||null===a||f<d)
											d=f,a=g;
										return c.splice(a,1)[0]};
										d.arrIndexOf=function(c,b){var a,d,g,f;
											if(null!=c.indexOf)
												return c.indexOf(b);a=g=0;
											for(f=c.length;g<f;a=++g)
												if(d=c[a],d===b)
													return a;
												return-1
											};
											return n
										}())
}).call(this);}).call(this);
/* Mon 14 Oct 2013 10:54:59 BST */