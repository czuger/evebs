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

      desc "Update prices history for main trade regions"
      task :main_trade_regions => :environment do
        puts 'About update to prices history for main trade regions'
        Crest::GetPriceHistory.new(true).regionset_update( Crest::GetPriceHistory::MAIN_TRADE_REGIONS )
      end

      desc "Update prices history for lesser trade regions"
      task :lesser_trade_regions => :environment do
        puts 'About to prices history for lesser trade regions'
        Crest::GetPriceHistory.new(true).regionset_update( Crest::GetPriceHistory::LESSER_TRADE_REGIONS )
      end

      desc "Update prices history for marginal trade regions"
      task :marginal_trade_regions => :environment do
        puts 'About to prices history for marginal trade regions'
        Crest::GetPriceHistory.new(true).regionset_update( Crest::GetPriceHistory::MARGINAL_TRADE_REGIONS )
      end

      desc "Update prices history for unknown trade regions"
      task :unknown_trade_regions => :environment do
        puts 'About to prices history for unknown trade regions'
        Crest::GetPriceHistory.new(true).regionset_update( Crest::GetPriceHistory::UNKNOWN_TRADE_REGIONS )
      end

    end
  end
end

namespace :data_setup do
  namespace :price_history do
    desc "Init price history"
    task :init => :environment do
      puts 'About to prices history'
      Crest::GetPriceHistory.new(true).regionset_update( Crest::GetPriceHistory::MAIN_TRADE_REGIONS )
    end
  end
end