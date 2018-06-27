namespace :setup do

  desc "Load blueprints"
  task :blueprints => :environment do
    Esi::UpdateBlueprints.new( nil ).update

    Esi::DownloadEveItems.new(debug_request: false ).update

  end

end
