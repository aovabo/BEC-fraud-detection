import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { toast } from "react-hot-toast";

export default function SafeWireDashboard() {
  const [apiKey, setApiKey] = useState("");
  const [amount, setAmount] = useState("");
  const [payeeId, setPayeeId] = useState("");
  const [balance, setBalance] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchBalance();
    fetchTransactions();
  }, []);

  const fetchBalance = async () => {
    try {
      const res = await fetch("/api/check_agent_balance");
      const data = await res.json();
      if (data.status === "Success") {
        setBalance(data.agent_balance);
      }
    } catch (error) {
      toast.error("Failed to fetch balance");
    }
  };

  const fetchTransactions = async () => {
    try {
      const res = await fetch("/api/transactions");
      const data = await res.json();
      setTransactions(data.transactions);
    } catch (error) {
      toast.error("Failed to fetch transactions");
    }
  };

  const handleSendPayment = async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/send_payment", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          paymentDestinationId: payeeId,
          amountDecimal: parseFloat(amount),
          memo: "Invoice Payment",
        }),
      });

      const data = await res.json();
      if (data.status === "Success") {
        toast.success("Payment sent successfully!");
        fetchTransactions();
      } else {
        toast.error(data.error);
      }
    } catch (error) {
      toast.error("Payment failed");
    }
    setLoading(false);
  };

  return (
    <div className="p-6 max-w-3xl mx-auto">
      <Card>
        <CardHeader>
          <CardTitle>SafeWire AI - Dashboard</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="mb-4">
            <p className="text-lg font-semibold">Agent Balance: ${balance ?? "Loading..."}</p>
          </div>
          <div className="space-y-3">
            <Input
              placeholder="Enter API Key"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
            />
            <Input
              placeholder="Enter Amount"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
            />
            <Input
              placeholder="Enter Payee ID"
              value={payeeId}
              onChange={(e) => setPayeeId(e.target.value)}
            />
            <Button onClick={handleSendPayment} disabled={loading}>
              {loading ? "Processing..." : "Send Payment"}
            </Button>
          </div>
          <div className="mt-6">
            <h2 className="text-xl font-semibold mb-2">Recent Transactions</h2>
            <ul className="list-disc pl-5">
              {transactions.length > 0 ? (
                transactions.map((tx, index) => (
                  <li key={index} className="text-sm">{tx.description} - ${tx.amount}</li>
                ))
              ) : (
                <p>No transactions found</p>
              )}
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
