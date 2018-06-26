namespace :setup do

  desc "Load blueprints"
  task :blueprints => :environment do
    Blueprint.load_blueprints
  end

end
