Rails.application.routes.draw do

  resource :admin_tools, only: [ :show ] do
    get :denied
  end

  resources :items, only: [ :show ] do
    get :cost
  end

  resource :shopping_baskets, only: [ :show ]

  resources :jita_margins, only: [ :index, :update ]

  resource :sale_records, only: [:show ] do
    get :items_sums
    get :station_sums
    get :stations_items_sums
    resources :sales_records_clients, only: [ :index, :show ]
  end

  resources :identities

  resource :users, only: [:edit, :update] do
    get :edit_password
    post :change_password
  end

  namespace :price_advices do
    get :advice_prices
    get :advice_prices_monthly
    get :show_challenged_prices
    post :update_basket
  end

  get 'price_advices/:item_id/show_item_detail/' => 'price_advices#show_item_detail', as: 'price_advices_show_item_detail'

  resource :choose_trade_hubs, only: [:edit, :update]

  resource :choose_items, only: [ :edit ] do
    get :items_tree
    post :select_items
  end

  resource :sessions, only: [:new] do
  end

  match 'auth/:provider/callback', to: 'sessions#create', via: [:get, :post]
  match 'auth/failure', to: 'sessions#failure', via: [:get, :post]
  # match 'auth/failure', to: redirect('/'), via: [:get, :post]
  match 'signout', to: 'sessions#destroy', as: 'signout', via: [:get, :post]

  root 'jita_margins#index'

end
