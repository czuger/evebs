class EveClient < ActiveRecord::Base

  def self.get_client( cpp_client_id, name )
    where( cpp_client_id: cpp_client_id ).first_or_create do |client|
      client.name = name
      client.cpp_client_id = cpp_client_id
    end
  end

end
