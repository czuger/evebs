namespace :data_setup do
  desc "Update the structures "
  task :structures => :environment do
    Esi::UpdateStructures.new( debug_request: false ).update
  end
end