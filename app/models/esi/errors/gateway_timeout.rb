module Esi::Errors
  class GatewayTimeout < Base

    def pause
      sleep 30
    end

  end
end