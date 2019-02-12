Rails.application.routes.draw do

  namespace :market_data do
    get ':item_id/trade_hub_detail/:trade_hub_id', action: :trade_hub_detail, as: :trade_hub_detail
    get ':item_id/market_overview/', action: :market_overview, as: :market_overview
  end

  resources :production_costs, only: [ :show ] do
    get :market_histories
  end
  get 'production_costs/:item_id/dailies_avg_prices/:trade_hub_id', controller: :production_costs, action: :dailies_avg_prices, as: :production_cost_dailies_avg_prices

  resource :helps, only: [:show ]

  resource :buy_orders, only: [:show]

  resource :my_assets, only: [:show, :update ] do
    post :set_assets_station
  end

  resources :user_to_user_duplication_requests, except: [ :edit, :update, :show ] do
    get :use
  end

  resource :admin_tools, only: [ :show ] do
    get :denied
    get :activity
    get :min_prices_timings
    get :min_prices_timings_overview
    get :items_users
    get :crest_price_history_update
  end

  resource :production_lists, only: [ :edit, :update, :create ] do
    put :update_from_components_to_buy

    post :create_from_prices_advices_immediate
    post :create_from_prices_advices_weekly
    post :create_from_prices_advices_buy_orders
  end
  post :remove_production_list_check, controller: :production_lists

  resource :user_sales_orders, only: [:show, :update ]

  resource :blueprints, only: [:show, :update]

  resource :components_to_buys, only: [:show, :update ]
  get :components_to_buy_show_raw,  controller: :components_to_buys

  resources :items, only: [ :show ]

  get :items_tree, controller: :items
  patch :items_tree_select, controller: :items

  resource :list_items, only: [ :edit, :update ] do
    get :my_items_list
    post :selection_change

    get :clear
    get :all

    post :save
    get ':saved_list_id/restore', action: :restore, as: :restore
    get :saved_list
  end

  resource :users, only: [:edit, :update] do
    patch :update_user_sales_orders_margin_filter
  end

  namespace :price_advices do
    get :advice_prices
    get :advice_prices_weekly
    get :empty_places
  end

  resource :miscs, only: [] do
    get :dev_log
  end

  resource :choose_trade_hubs, only: [:edit, :update]

  match 'auth/:provider/callback', to: 'sessions#create', via: [:get, :post]
  match 'auth/failure', to: 'sessions#failure', via: [:get, :post]
  # match 'auth/failure', to: redirect('/'), via: [:get, :post]
  match 'signout', to: 'sessions#destroy', as: 'signout', via: [:get, :post]

  root 'jita_margins#index'

end
