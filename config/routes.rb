Rails.application.routes.draw do

  resources :identities

  resource :user, only: [:edit,:update]

  resource :price_advices, only: [:show]
  resource :choose_trade_hubs, only: [:edit, :update]

  resource :choose_items, only: [:new, :edit, :create, :update] do
    get :autocomplete_eve_item_name_lowcase, :on => :collection
  end

  resource :sessions, only: [:new]
  match 'auth/:provider/callback', to: 'sessions#create', via: [:get, :post]
  match 'auth/failure', to: redirect('/'), via: [:get, :post]
  match 'signout', to: 'sessions#destroy', as: 'signout', via: [:get, :post]

  root 'choose_items#edit'

end
