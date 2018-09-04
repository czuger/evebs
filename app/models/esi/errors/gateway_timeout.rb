module Esi::Errors
  class GatewayTimeout < Base

    def pause
      sleep 30
    end

    def retry?
      true
    end

  end
end