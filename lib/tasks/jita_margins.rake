namespace :data_compute do
  desc "Recompute all jita margins for front page"
  task :jita_margins => :environment do

    Rake::Task[ 'data_compute:min_prices:jita' ].invoke

    puts '*'*100
    puts 'About to compute jita margin'
    puts '*'*100
    JitaMargin.compute_margins
    puts '*'*100
    puts 'About to compute jita margin'
    puts '*'*100

  end
end