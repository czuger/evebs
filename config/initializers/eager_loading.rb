if %w( production staging ).include?( Rails.env )
  Rails.application.eager_load!
end
