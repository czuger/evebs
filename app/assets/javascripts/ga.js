document.addEventListener("turbolinks:load", function() {

	var railsEnv = $('body').data( 'rails-env' );

	if( railsEnv != 'development' ){
		(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
				(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
			m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
		})(window,document,'script','//www.google-analytics.com/analytics.js','ga');

		ga('create', 'UA-15363494-4', 'auto');
		ga('send', 'pageview');

	}

});





