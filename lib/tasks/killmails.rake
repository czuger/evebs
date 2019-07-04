namespace :killmails do

  desc 'Update killmails data'
  task :update => :environment do
    Misc::Killmails.new.update
  end

end