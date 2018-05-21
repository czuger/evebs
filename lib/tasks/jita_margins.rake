# namespace :data_compute do
#
#   desc "Recompute all jita margins for front page"
#   task :jita_margins => :environment do
#
#     Rake::Task[ 'data_compute:min_prices:jita' ].invoke
#
#     puts '*'*100
#     puts 'About to compute jita margin'
#     puts '*'*100
#     JitaMargin.compute_margins
#
#     # At the end we need to clear the cache (the front page)
#     File.unlink( 'public/index.html' ) if File.exists?( 'public/index.html' )
#   end
# end
#
# namespace :data_setup do
#
#   desc "Set well know epic blueprints"
#   task :set_epic_blueprints => :environment do
#
#     epic_patterns = [ '%Republic%', '%Federation Navy%' ]
#     epic_patterns.each do |pattern|
#       EveItem.where( 'name LIKE ?', pattern ).each do |item|
#         puts "Setting epic blueprint to #{item.name}"
#         item.update_attribute( :epic_blueprint, true )
#       end
#     end
#   end
# end