Rails.application.routes.draw do

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

  resources :production_lists, only: [ :edit, :update, :create ]
  post :remove_production_list_check, controller: :production_lists

  resource :user_sales_orders, only: [:show, :update ]

  resource :blueprints, only: [:show, :update]

  resources :components_to_buy, only: [ :show ]
  get :components_to_buy_show_raw,  controller: :components_to_buy

  resources :items, only: [ :show ] do
    get :cost
    get :trade_hub_detail
  end

  get :items_tree, controller: :items
  patch :items_tree_select, controller: :items

  resource :list_items, only: [ :edit, :update ] do
    get :my_items_list
  end

  resource :users, only: [:edit, :update] do
    patch :update_user_sales_orders_margin_filter
  end

  namespace :price_advices do
    get :advice_prices
    get :advice_prices_weekly
    get :empty_places
  end

  resource :choose_trade_hubs, only: [:edit, :update]

  match 'auth/:provider/callback', to: 'sessions#create', via: [:get, :post]
  match 'auth/failure', to: 'sessions#failure', via: [:get, :post]
  # match 'auth/failure', to: redirect('/'), via: [:get, :post]
  match 'signout', to: 'sessions#destroy', as: 'signout', via: [:get, :post]

  root 'jita_margins#index'

end
