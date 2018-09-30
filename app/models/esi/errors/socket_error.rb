module Esi::Errors
  class SocketError < Base

    def pause
      sleep 60
    end

    def retry?
      true
    end

  end
end