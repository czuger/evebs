namespace :data_compute do
  namespace :price_history do
    namespace :update do

      desc "Update price history (Jita + marked by users)"
      task :all => :environment do
        puts 'About to update price history'
        gph = Crest::GetPriceHistory.new
        gph.get_jita_components_prices
        gph.get_watched_items_and_region_only
      end

      desc "Update prices history (marked by users only)"
      task :used => :environment do
        puts 'About to prices history'
        gph = Crest::GetPriceHistory.new
        gph.get_watched_items_and_region_only
      end

    end
  end
end

namespace :data_setup do
  namespace :price_history do
    desc "Init price history"
    task :init => :environment do
      puts 'About to prices history'
      Crest::GetPriceHistory.new(true).full_update
    end
  end
end