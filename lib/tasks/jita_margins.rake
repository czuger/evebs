namespace :data_compute do
  desc "Recompute all jita margins for front page"
  task :jita_margins => :environment do

    JitaMargin.compute_margins

  end
end