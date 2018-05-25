# namespace :process do
#   desc 'Full data setup'
#   task :full => [:environment, :trade_hubs, :regions, 'price_history:init', :update_all_items, :blueprints_setup, :stations, :market_groups]
# end

namespace :process do
  namespace :full do
    desc 'Full process - hourly'
    # task :hourly => [:environment, :min_prices, :get_orders, :prices_advices, :jita_margins ]
    # task :hourly => [:environment, :print_time, :min_prices, :prices_advices, :jita_margins, :print_time ]
    task :hourly => [:environment, :print_time, :min_prices, :prices_advices, :print_time ]

    desc 'Full process - daily'
    # TODO, revoir le process, faire le calcul des couts avant la creation du nouveau arbre d'objets.
    task :weekly => [:environment, :print_time, :update_all_items, :eve_markets_histories, :compute_prices_history_average, :costs, :print_time ]
  end
end